from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openpyxl import load_workbook

from app.services.workbook_service import WorkbookService

router = APIRouter(prefix="/excel", tags=["Excel"])

workbook_service = WorkbookService()


@router.get("/test")
def test_excel_router():
    return {"message": "Excel router works"}


@router.post("/upload")
async def upload_excel(
    file: UploadFile = File(...),
    selected_sheet: str | None = Form(default=None),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xlsm files are allowed")

    file_bytes = await file.read()

    workbook_record = workbook_service.create_workbook(
        file_bytes=file_bytes,
        original_filename=file.filename,
    )

    try:
        workbook = load_workbook(workbook_record["file_path"], data_only=False)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Excel file could not be read: {str(error)}"
        )

    sheets = []

    for sheet in workbook.worksheets:
        sheets.append({
            "name": sheet.title,
            "rows": sheet.max_row,
            "columns": sheet.max_column,
        })

    if selected_sheet:
        if selected_sheet not in workbook.sheetnames:
            raise HTTPException(
                status_code=400,
                detail=f"Sheet not found: {selected_sheet}"
            )
        active_sheet = workbook[selected_sheet]
    else:
        active_sheet = workbook.worksheets[0]

    grid_data = worksheet_to_grid_data(active_sheet)

    return {
        "message": "Excel file uploaded and read successfully",
        "workbook_id": workbook_record["workbook_id"],
        "original_filename": file.filename,
        "stored_filename": workbook_record["stored_filename"],
        "sheet_count": len(workbook.worksheets),
        "sheets": sheets,
        "active_sheet": active_sheet.title,
        "columns": grid_data["columns"],
        "rows": grid_data["rows"],
    }


def worksheet_to_grid_data(sheet, max_rows: int = 200):
    rows = list(sheet.iter_rows(values_only=True))

    if not rows:
        return {
            "columns": [],
            "rows": []
        }

    header_row = rows[0]
    columns = []

    for index, header in enumerate(header_row):
        if header is None or str(header).strip() == "":
            field_name = f"column_{index + 1}"
            header_name = f"Column {index + 1}"
        else:
            field_name = normalize_field_name(str(header), index)
            header_name = str(header)

        columns.append({
            "field": field_name,
            "headerName": header_name,
            "editable": True,
            "filter": True,
            "sortable": True,
            "resizable": True,
        })

    data_rows = []

    for row_index, row in enumerate(rows[1:max_rows + 1], start=1):
        row_object = {}

        for column_index, cell_value in enumerate(row):
            if column_index >= len(columns):
                continue

            field_name = columns[column_index]["field"]

            if cell_value is None:
                row_object[field_name] = ""
            else:
                row_object[field_name] = cell_value

        row_object["_rowNumber"] = row_index
        data_rows.append(row_object)

    return {
        "columns": columns,
        "rows": data_rows
    }


def normalize_field_name(value: str, index: int) -> str:
    field = value.strip().lower()

    replacements = {
        " ": "_",
        "-": "_",
        "/": "_",
        "\\": "_",
        ".": "_",
        ",": "_",
        "(": "",
        ")": "",
        "%": "percent",
        "₺": "try",
        "$": "usd",
        "€": "eur",
    }

    for old, new in replacements.items():
        field = field.replace(old, new)

    field = "".join(char for char in field if char.isalnum() or char == "_")

    if not field:
        field = f"column_{index + 1}"

    return field