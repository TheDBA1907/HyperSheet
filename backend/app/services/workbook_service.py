from pathlib import Path
from uuid import uuid4


class WorkbookService:

    def create_workbook(self, file_bytes: bytes, original_filename: str):
        workbook_id = uuid4().hex

        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)

        stored_filename = f"{workbook_id}_{original_filename}"

        file_path = uploads_dir / stored_filename

        file_path.write_bytes(file_bytes)

        return {
            "workbook_id": workbook_id,
            "stored_filename": stored_filename,
            "file_path": file_path,
        }