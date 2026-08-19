let gridApi = null;
let currentExcelFile = null;
let currentActiveSheet = null;

let selectionStartCell = null;
let selectionEndCell = null;
let isSelectingCells = false;

const EMPTY_ROW_COUNT = 1000;
const EMPTY_COLUMN_COUNT = 100;

document.addEventListener("DOMContentLoaded", function () {
    const gridElement = document.querySelector("#hypersheet-grid");

    if (!gridElement) {
        console.error("HyperSheet grid element could not be found.");
        return;
    }

    const gridOptions = {
        columnDefs: createGridColumns(createEmptyColumns()),
        rowData: createEmptyRows(EMPTY_ROW_COUNT),

        defaultColDef: {
            sortable: false,
            filter: false,
            resizable: true,
            editable: true,
            width: 100,
            minWidth: 60,
            maxWidth: 400,
            cellClass: getCellSelectionClass,
        },

        rowSelection: "multiple",
        animateRows: false,
        enableCellTextSelection: true,
        suppressRowClickSelection: true,

        tabToNextCell: tabToNextCell,

        onCellMouseDown: handleCellMouseDown,
        onCellMouseOver: handleCellMouseOver,
        onCellClicked: handleCellClicked,

        onGridReady: function (params) {
            gridApi = params.api;
            focusFirstEditableCell();
        }
    };

    gridApi = agGrid.createGrid(gridElement, gridOptions);

gridElement.addEventListener(
    "keydown",
    handleGridNavigationKey,
    true,
  handleClipboardKeyDown,
    true
);

document.addEventListener(
    "mouseup",
    handleDocumentMouseUp
);
setupExcelImport();
});

function navigateToNextCell(params) {
    const previousCell = params.previousCellPosition;
    const suggestedCell = params.nextCellPosition;

    if (!previousCell) {
        return suggestedCell;
    }

    if (params.key !== "Enter") {
        return suggestedCell;
    }

    const shiftPressed =
        params.event &&
        params.event.shiftKey === true;

    const direction = shiftPressed ? -1 : 1;
    const nextRowIndex = previousCell.rowIndex + direction;
    const rowCount = params.api.getDisplayedRowCount();

    if (nextRowIndex < 0 || nextRowIndex >= rowCount) {
        return previousCell;
    }

    return {
        rowIndex: nextRowIndex,
        rowPinned: previousCell.rowPinned,
        column: previousCell.column
    };
}

function tabToNextCell(params) {
    const nextCell = params.nextCellPosition;

    if (!nextCell) {
        return params.previousCellPosition;
    }

    if (nextCell.column.getColId() === "rowNumber") {
        const displayedColumns = params.api.getAllDisplayedColumns();
        const firstDataColumn = displayedColumns.find(function (column) {
            return column.getColId() !== "rowNumber";
        });

        if (!firstDataColumn) {
            return params.previousCellPosition;
        }

        return {
            rowIndex: nextCell.rowIndex,
            rowPinned: nextCell.rowPinned,
            column: firstDataColumn
                    };
    }

    return nextCell;
}

function focusFirstEditableCell() {
    if (!gridApi) {
        return;
    }

    const displayedColumns = gridApi.getAllDisplayedColumns();

    const firstEditableColumn = displayedColumns.find(function (column) {
        return column.getColId() !== "rowNumber";
    });

    if (!firstEditableColumn) {
        return;
    }

    setTimeout(function () {
        gridApi.setFocusedCell(
            0,
            firstEditableColumn.getColId()
        );
    }, 0);
}

function createRowNumberColumn() {
    return {
        headerName: "",
        colId: "rowNumber",

        valueGetter: function (params) {
            if (!params.node) {
                return "";
            }

            return params.node.rowIndex + 1;
        },

        width: 48,
        minWidth: 48,
        maxWidth: 48,

        pinned: "left",
        lockPosition: true,
        lockPinned: true,

        suppressMovable: true,
        suppressNavigable: true,

        sortable: false,
        filter: false,
        editable: false,
        resizable: false,

        cellClass: "row-number-cell",
        headerClass: "row-number-header"
    };
}

function createGridColumns(dataColumns) {
    return [
        createRowNumberColumn(),
        ...dataColumns
    ];
}

function createEmptyColumns() {
    const columns = [];

    for (
        let columnIndex = 1;
        columnIndex <= EMPTY_COLUMN_COUNT;
        columnIndex++
    ) {
        columns.push({
            headerName: getExcelColumnName(columnIndex),
            field: `col_${columnIndex}`,
            colId: `col_${columnIndex}`,

            width: 100,
            minWidth: 60,
            maxWidth: 400,

            editable: true,
            sortable: false,
            filter: false,
            resizable: true,

            suppressMovable: false
        });
    }

    return columns;
}

function createEmptyRows(rowCount) {
    const rows = [];

    for (
        let rowIndex = 0;
        rowIndex < rowCount;
        rowIndex++
    ) {
        const row = {};

        for (
            let columnIndex = 1;
            columnIndex <= EMPTY_COLUMN_COUNT;
            columnIndex++
        ) {
            row[`col_${columnIndex}`] = "";
        }

        rows.push(row);
    }

    return rows;
}

function getExcelColumnName(index) {
    let name = "";
    let number = index;

    while (number > 0) {
        const remainder = (number - 1) % 26;

        name =
            String.fromCharCode(65 + remainder) +
            name;

        number = Math.floor(
            (number - 1) / 26
        );
    }

    return name;
}

function setupExcelImport() {
    const importButton =
        document.querySelector("#importExcelButton");

    const fileInput =
        document.querySelector("#excelFileInput");

    if (!importButton || !fileInput) {
        console.error(
            "Excel import controls could not be found."
        );

        return;
    }
    importButton.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", async function () {
        const file = fileInput.files[0];

        if (!file) {
            return;
        }

        currentExcelFile = file;

        await uploadExcelFile(file, null);

        fileInput.value = "";
    });
}

async function uploadExcelFile(file, selectedSheet) {
    const formData = new FormData();

    formData.append("file", file);

    if (selectedSheet) {
        formData.append(
            "selected_sheet",
            selectedSheet
        );
    }

    try {
        setPageTitle("Loading sheet...");

        const response = await fetch(
            "/api/v1/excel/upload",
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            const errorText = await response.text();

            throw new Error(errorText);
        }

        const data = await response.json();

        console.log(
            "Excel import response:",
            data
        );

        const importedColumns =
            normalizeImportedColumns(data.columns);

        const importedRows =
            normalizeImportedRows(data.rows);

        gridApi.setGridOption(
            "columnDefs",
            createGridColumns(importedColumns)
        );

        gridApi.setGridOption(
            "rowData",
            importedRows
        );

        currentActiveSheet =
            data.active_sheet || null;

        const filename =
            data.original_filename || file.name;

        const sheetName =
            data.active_sheet || "Sheet";

        setPageTitle(
            `${filename} / ${sheetName}`
        );

        renderSheetList(
            Array.isArray(data.sheets)
                ? data.sheets
                : [],
            data.active_sheet
        );

        focusFirstEditableCell();
    } catch (error) {
        console.error(
            "Excel import failed:",
            error
        );

        alert(
            "Excel import failed. Press F12 and check the Console for details."
        );

        setPageTitle(
            "Semantic Data Workspace"
        );
    }
}

function normalizeImportedRows(rows) {
    if (!Array.isArray(rows)) {
        return createEmptyRows(
            EMPTY_ROW_COUNT
        );
    }

    if (rows.length === 0) {
        return createEmptyRows(
            EMPTY_ROW_COUNT
        );
    }

    const normalizedRows = rows.map(
        function (row) {
            return row && typeof row === "object"
                ? { ...row }
                : {};
        }
    );

    const missingRowCount =
        EMPTY_ROW_COUNT - normalizedRows.length;
    if (missingRowCount > 0) {
        const emptyRows = createEmptyRows(
            missingRowCount
        );

        normalizedRows.push(
            ...emptyRows
        );
    }

    return normalizedRows;
}

function normalizeImportedColumns(columns) {
    if (
        !Array.isArray(columns) ||
        columns.length === 0
    ) {
        return createEmptyColumns();
    }

    return columns.map(
        function (column, index) {
            if (
                typeof column === "object" &&
                column !== null &&
                !Array.isArray(column)
            ) {
                return {
                    ...column,

                    headerName:
                        column.headerName ||
                        column.field ||
                        getExcelColumnName(
                            index + 1
                        ),

                    field:
                        column.field ||
                        `col_${index + 1}`,

                    colId:
                        column.colId ||
                        column.field ||
                        `col_${index + 1}`,

                    width:
                        column.width ||
                        100,

                    minWidth:
                        column.minWidth ||
                        60,

                    maxWidth:
                        column.maxWidth ||
                        400,

                    editable:
                        column.editable !== undefined
                            ? column.editable
                            : true,

                    sortable:
                        column.sortable !== undefined
                            ? column.sortable
                            : true,

                    filter:
                        column.filter !== undefined
                            ? column.filter
                            : true,

                    resizable:
                        column.resizable !== undefined
                            ? column.resizable
                            : true
                };
            }

            const fieldName = String(column);

            return {
                headerName: fieldName,
                field: fieldName,
                colId: fieldName,

                width: 100,
                minWidth: 60,
                maxWidth: 400,

                editable: true,
                sortable: true,
                filter: true,
                resizable: true
            };
        }
    );
}

function renderSheetList(
    sheets,
    activeSheet
) {
    const sidebar =
        document.querySelector(".sidebar");

    if (!sidebar) {
        console.error(
            "Sidebar element could not be found."
        );

        return;
    }

    sidebar.innerHTML =
        "<h3>Sheets</h3>";

    sheets.forEach(function (sheet) {
        const section =
            document.createElement("div");

        section.className =
            "section sheet-item";

        if (
            sheet.name === activeSheet
        ) {
            section.classList.add(
                "active-sheet"
            );
        }

        section.innerHTML = `
            <h3>${escapeHtml(sheet.name)}</h3>

            <ul>
                <li>${sheet.rows ?? 0} rows</li>
                <li>${sheet.columns ?? 0} columns</li>
                <li>
                    ${
                        sheet.name === activeSheet
                            ? "Active sheet"
                            : "Click to open"
                    }
                </li>
            </ul>
        `;

        section.addEventListener(
            "click",
            async function () {
                if (!currentExcelFile) {
                    alert(
                        "Please import an Excel file first."
                    );

                    return;
                }

                if (
                    sheet.name === currentActiveSheet
                ) {
                    return;
                }

                await uploadExcelFile(
                    currentExcelFile,
                    sheet.name
                );
            }
        );

        sidebar.appendChild(section);
    });
}

function setPageTitle(title) {
    const titleElement =
        document.querySelector(".title");

    if (!titleElement) {
        return;
    }

    titleElement.innerText = title;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
function handleGridNavigationKey(event) {
    if (!gridApi) {
        return;
    }

    const supportedKeys = [
        "Enter",
        "Home",
        "End",
        "PageUp",
        "PageDown"
    ];

    if (!supportedKeys.includes(event.key)) {
        return;
    }

    const focusedCell = gridApi.getFocusedCell();

    if (!focusedCell) {
        return;
    }

    const displayedColumns = gridApi
        .getAllDisplayedColumns()
        .filter(function (column) {
            return column.getColId() !== "rowNumber";
        });

    if (displayedColumns.length === 0) {
        return;
    }

    const rowCount = gridApi.getDisplayedRowCount();

    if (rowCount === 0) {
        return;
    }

    const currentRowIndex = focusedCell.rowIndex;
    const currentColumnId = focusedCell.column.getColId();

    let targetRowIndex = currentRowIndex;
    let targetColumnId = currentColumnId;

    const controlPressed =
        event.ctrlKey === true ||
        event.metaKey === true;

    if (event.key === "Enter") {
        targetRowIndex =
            currentRowIndex +
            (event.shiftKey ? -1 : 1);
    }

    if (event.key === "Home") {
        targetColumnId =
            displayedColumns[0].getColId();

        if (controlPressed) {
            targetRowIndex = 0;
        }
    }

    if (event.key === "End") {
        targetColumnId =
            displayedColumns[
                displayedColumns.length - 1
            ].getColId();

        if (controlPressed) {
            targetRowIndex = rowCount - 1;
        }
    }

    if (event.key === "PageUp") {
        targetRowIndex =
            currentRowIndex - 20;
    }

    if (event.key === "PageDown") {
        targetRowIndex =
            currentRowIndex + 20;
    }

    targetRowIndex = Math.max(
        0,
        Math.min(
            targetRowIndex,
            rowCount - 1
        )
    );

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    gridApi.stopEditing();

    setTimeout(function () {
        gridApi.ensureIndexVisible(
            targetRowIndex,
            "middle"
        );

        gridApi.ensureColumnVisible(
            targetColumnId
        );

        gridApi.setFocusedCell(
            targetRowIndex,
            targetColumnId
        );
    }, 0);
}
function handleCellMouseDown(params) {
    if (!params.column || params.column.getColId() === "rowNumber") {
        return;
    }

    if (params.rowIndex == null) {
        return;
    }

    const mouseEvent = params.event;

    if (mouseEvent && mouseEvent.shiftKey && selectionStartCell) {
        selectionEndCell = {
            rowIndex: params.rowIndex,
            columnId: params.column.getColId()
        };
    } else {
        selectionStartCell = {
            rowIndex: params.rowIndex,
            columnId: params.column.getColId()
        };

        selectionEndCell = {
            rowIndex: params.rowIndex,
            columnId: params.column.getColId()
        };
    }

    isSelectingCells = true;

    refreshCellSelection();
}

function handleCellMouseOver(params) {
    if (!isSelectingCells) {
        return;
    }

    if (!params.column || params.column.getColId() === "rowNumber") {
        return;
    }

    if (params.rowIndex == null) {
        return;
    }

    selectionEndCell = {
        rowIndex: params.rowIndex,
        columnId: params.column.getColId()
    };

    refreshCellSelection();
}

function handleCellClicked(params) {
    if (!params.column || params.column.getColId() === "rowNumber") {
        return;
    }

    if (params.rowIndex == null) {
        return;
    }

    if (params.event && params.event.shiftKey && selectionStartCell) {
        selectionEndCell = {
            rowIndex: params.rowIndex,
            columnId: params.column.getColId()
        };

        refreshCellSelection();
    }
}

function handleDocumentMouseUp() {
    isSelectingCells = false;
}

function refreshCellSelection() {
    if (!gridApi || !selectionStartCell || !selectionEndCell) {
        return;
    }

    gridApi.refreshCells({
        force: true
    });
}

function getSelectionBounds() {
    if (!gridApi || !selectionStartCell || !selectionEndCell) {
        return null;
    }

    const displayedColumns = gridApi
        .getAllDisplayedColumns()
        .filter(function (column) {
            return column.getColId() !== "rowNumber";
        });

    const startColumnIndex = displayedColumns.findIndex(
        function (column) {
            return column.getColId() === selectionStartCell.columnId;
        }
    );

    const endColumnIndex = displayedColumns.findIndex(
        function (column) {
            return column.getColId() === selectionEndCell.columnId;
        }
    );

    if (startColumnIndex === -1 || endColumnIndex === -1) {
        return null;
    }

    return {
        firstRow: Math.min(
            selectionStartCell.rowIndex,
            selectionEndCell.rowIndex
        ),

        lastRow: Math.max(
            selectionStartCell.rowIndex,
            selectionEndCell.rowIndex
        ),

        firstColumn: Math.min(
            startColumnIndex,
            endColumnIndex
        ),

        lastColumn: Math.max(
            startColumnIndex,
            endColumnIndex
        ),

        displayedColumns: displayedColumns
    };
}

function getCellSelectionClass(params) {
    if (
        !params.column ||
        params.column.getColId() === "rowNumber" ||
        params.node.rowIndex == null
    ) {
        return "";
    }

    const bounds = getSelectionBounds();

    if (!bounds) {
        return "";
    }

    const columnIndex = bounds.displayedColumns.findIndex(
        function (column) {
            return column.getColId() === params.column.getColId();
        }
    );

    const rowIndex = params.node.rowIndex;

    const isSelected =
        rowIndex >= bounds.firstRow &&
        rowIndex <= bounds.lastRow &&
        columnIndex >= bounds.firstColumn &&
        columnIndex <= bounds.lastColumn;

    if (!isSelected) {
        return "";
    }

    const classes = [
        "hypersheet-selected-cell"
    ];

    if (rowIndex === bounds.firstRow) {
        classes.push("hypersheet-selection-top");
    }

    if (rowIndex === bounds.lastRow) {
        classes.push("hypersheet-selection-bottom");
    }

    if (columnIndex === bounds.firstColumn) {
        classes.push("hypersheet-selection-left");
    }

    if (columnIndex === bounds.lastColumn) {
        classes.push("hypersheet-selection-right");
    }

    if (
        selectionStartCell &&
        rowIndex === selectionStartCell.rowIndex &&
        params.column.getColId() === selectionStartCell.columnId
    ) {
        classes.push("hypersheet-active-cell");
    }

    return classes.join(" ");
}

function handleClipboardKeyDown(event) {
    if (!gridApi) {
        return;
    }

    if (isTextEditorTarget(event.target)) {
        return;
    }

    const controlPressed =
        event.ctrlKey === true ||
        event.metaKey === true;

    const key = event.key.toLowerCase();

    if (controlPressed && key === "c") {
        event.preventDefault();
        copySelectedCells(false);
        return;
    }

    if (controlPressed && key === "x") {
        event.preventDefault();
        copySelectedCells(true);
        return;
    }

    if (controlPressed && key === "v") {
        event.preventDefault();
        pasteIntoSelectedCell();
        return;
    }

    if (
        event.key === "Delete" ||
        event.key === "Backspace"
    ) {
        event.preventDefault();
        clearSelectedCells();
    }
}

function isTextEditorTarget(target) {
    if (!target) {
        return false;
    }

    const tagName =
        target.tagName
            ? target.tagName.toLowerCase()
            : "";

    return (
        tagName === "input" ||
        tagName === "textarea" ||
        target.isContentEditable === true
    );
}

async function copySelectedCells(clearAfterCopy) {
    const clipboardText =
        buildSelectedCellsClipboardText();

    if (clipboardText === null) {
        return;
    }

    try {
        await navigator.clipboard.writeText(
            clipboardText
        );

        if (clearAfterCopy) {
            clearSelectedCells();
        }
    } catch (error) {
        console.error(
            "Clipboard copy failed:",
            error
        );

        fallbackCopyText(
            clipboardText
        );

        if (clearAfterCopy) {
            clearSelectedCells();
        }
    }
}

function buildSelectedCellsClipboardText() {
    const bounds = getSelectionBounds();

    if (!bounds) {
        return buildFocusedCellClipboardText();
    }

    const clipboardRows = [];

    for (
        let rowIndex = bounds.firstRow;
        rowIndex <= bounds.lastRow;
        rowIndex++
    ) {
        const rowNode =
            gridApi.getDisplayedRowAtIndex(
                rowIndex
            );

        if (!rowNode) {
            continue;
        }

        const clipboardColumns = [];

        for (
            let columnIndex = bounds.firstColumn;
            columnIndex <= bounds.lastColumn;
            columnIndex++
        ) {
            const column =
                bounds.displayedColumns[
                    columnIndex
                ];

            const value =
                gridApi.getCellValue({
                    rowNode: rowNode,
                    colKey: column
                });

            clipboardColumns.push(
                normalizeClipboardValue(value)
            );
        }

        clipboardRows.push(
            clipboardColumns.join("\t")
        );
    }

    return clipboardRows.join("\n");
}

function buildFocusedCellClipboardText() {
    const focusedCell =
        gridApi.getFocusedCell();

    if (
        !focusedCell ||
        focusedCell.column.getColId() ===
            "rowNumber"
    ) {
        return null;
    }

    const rowNode =
        gridApi.getDisplayedRowAtIndex(
            focusedCell.rowIndex
        );

    if (!rowNode) {
        return null;
    }

    const value =
        gridApi.getCellValue({
            rowNode: rowNode,
            colKey: focusedCell.column
        });

    return normalizeClipboardValue(value);
}

function normalizeClipboardValue(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("\r\n", "\n")
        .replaceAll("\r", "\n");
}

function fallbackCopyText(text) {
    const textArea =
        document.createElement("textarea");

    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    textArea.style.pointerEvents = "none";

    document.body.appendChild(textArea);

    textArea.focus();
    textArea.select();

    document.execCommand("copy");

    document.body.removeChild(textArea);
}

async function pasteIntoSelectedCell() {
    let clipboardText;

    try {
        clipboardText =
            await navigator.clipboard.readText();
    } catch (error) {
        console.error(
            "Clipboard read failed:",
            error
        );

        alert(
            "Clipboard could not be read. Please allow clipboard access in the browser."
        );

        return;
    }

    if (!clipboardText) {
        return;
    }

    pasteClipboardText(
        clipboardText
    );
}

function pasteClipboardText(text) {
    const startCell =
        selectionStartCell ||
        getFocusedCellPosition();

    if (!startCell) {
        return;
    }

    const displayedColumns = gridApi
        .getAllDisplayedColumns()
        .filter(function (column) {
            return (
                column.getColId() !==
                "rowNumber"
            );
        });

    const startColumnIndex =
        displayedColumns.findIndex(
            function (column) {
                return (
                    column.getColId() ===
                    startCell.columnId
                );
            }
        );

    if (startColumnIndex === -1) {
        return;
    }

    const clipboardRows = text
        .replaceAll("\r\n", "\n")
        .replaceAll("\r", "\n")
        .split("\n");

    if (
        clipboardRows.length > 1 &&
        clipboardRows[
            clipboardRows.length - 1
        ] === ""
    ) {
        clipboardRows.pop();
    }

    let lastRowIndex =
        startCell.rowIndex;

    let lastColumnIndex =
        startColumnIndex;

    clipboardRows.forEach(
        function (clipboardRow, rowOffset) {
            const targetRowIndex =
                startCell.rowIndex +
                rowOffset;

            const rowNode =
                gridApi.getDisplayedRowAtIndex(
                    targetRowIndex
                );

            if (!rowNode) {
                return;
            }

            const clipboardColumns =
                clipboardRow.split("\t");

            clipboardColumns.forEach(
                function (
                    clipboardValue,
                    columnOffset
                ) {
                    const targetColumnIndex =
                        startColumnIndex +
                        columnOffset;

                    const targetColumn =
                        displayedColumns[
                            targetColumnIndex
                        ];

                    if (!targetColumn) {
                        return;
                    }

                    rowNode.setDataValue(
                        targetColumn,
                        clipboardValue
                    );

                    lastRowIndex =
                        Math.max(
                            lastRowIndex,
                            targetRowIndex
                        );

                    lastColumnIndex =
                        Math.max(
                            lastColumnIndex,
                            targetColumnIndex
                        );
                }
            );
        }
    );

    selectionStartCell = {
        rowIndex: startCell.rowIndex,
        columnId:
            displayedColumns[
                startColumnIndex
            ].getColId()
    };

    selectionEndCell = {
        rowIndex: lastRowIndex,
        columnId:
            displayedColumns[
                lastColumnIndex
            ].getColId()
    };

    gridApi.refreshCells({
        force: true
    });

    gridApi.setFocusedCell(
        startCell.rowIndex,
        startCell.columnId
    );
}

function clearSelectedCells() {
    const bounds =
        getSelectionBounds();

    if (!bounds) {
        clearFocusedCell();
        return;
    }

    for (
        let rowIndex = bounds.firstRow;
        rowIndex <= bounds.lastRow;
        rowIndex++
    ) {
        const rowNode =
            gridApi.getDisplayedRowAtIndex(
                rowIndex
            );

        if (!rowNode) {
            continue;
        }

        for (
            let columnIndex =
                bounds.firstColumn;
            columnIndex <=
                bounds.lastColumn;
            columnIndex++
        ) {
            const column =
                bounds.displayedColumns[
                    columnIndex
                ];

            rowNode.setDataValue(
                column,
                ""
            );
        }
    }

    gridApi.refreshCells({
        force: true
    });
}

function clearFocusedCell() {
    const focusedCell =
        gridApi.getFocusedCell();

    if (
        !focusedCell ||
        focusedCell.column.getColId() ===
            "rowNumber"
    ) {
        return;
    }

    const rowNode =
        gridApi.getDisplayedRowAtIndex(
            focusedCell.rowIndex
        );

    if (!rowNode) {
        return;
    }

    rowNode.setDataValue(
        focusedCell.column,
        ""
    );

    gridApi.refreshCells({
        rowNodes: [rowNode],
        columns: [
            focusedCell.column
        ],
        force: true
    });
}

function getFocusedCellPosition() {
    const focusedCell =
        gridApi.getFocusedCell();

    if (
        !focusedCell ||
        focusedCell.column.getColId() ===
            "rowNumber"
    ) {
        return null;
    }

    return {
        rowIndex:
            focusedCell.rowIndex,

        columnId:
            focusedCell.column.getColId()
    };
}