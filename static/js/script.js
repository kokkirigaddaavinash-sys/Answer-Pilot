const questionInput = document.getElementById("questionInput");
const generateButton = document.getElementById("generateButton");
const answerOutput = document.getElementById("answerOutput");

const copyAnswerButton = document.getElementById("copyAnswerButton");
const regenerateButton = document.getElementById("regenerateButton");
const downloadAnswerButton = document.getElementById("downloadAnswerButton");

const notesPreview = document.getElementById("notesPreview");
const downloadNotesButton = document.getElementById("downloadNotesButton");

const previousPageButton = document.getElementById("previousPage");
const nextPageButton = document.getElementById("nextPage");
const pageCounter = document.getElementById("pageCounter");

const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const fileCount = document.getElementById("fileCount");

const languageSelect = document.getElementById("languageSelect");
const lengthSelect = document.getElementById("lengthSelect");

const answerStatus = document.getElementById("answerStatus");

const answerTypeButtons =
    document.querySelectorAll(".answer-type");

let lastQuestion = "";
let lastAnswer = "";

let selectedAnswerType = "exam";

let uploadedFiles = [];

let notePages = [];
let currentPage = 0;

/* ============================================================
ANSWER TYPE
============================================================ */

answerTypeButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        answerTypeButtons.forEach(function (item) {
            item.classList.remove("active");
        });

        button.classList.add("active");

        selectedAnswerType =
            button.getAttribute("data-type") || "exam";
    });

});

function getAnswerType() {

    if (selectedAnswerType === "simple") {
        return "2 Marks";
    }

    if (selectedAnswerType === "detailed") {
        return "10 Marks";
    }

    if (selectedAnswerType === "points") {
        return "Key Points";
    }

    return "5 Marks";
}

/* ============================================================
GENERATE
============================================================ */

async function generateAnswer() {

    if (!questionInput) {
        return;
    }

    const question = questionInput.value.trim();

    if (!question) {
        alert("Please enter your question.");
        questionInput.focus();
        return;
    }

    lastQuestion = question;

    setLoading(true);

    showAnswerLoading();
    showNotesLoading();
    setStatus("GENERATING");

    try {

        const response = await fetch("/ask", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                question: question,

                answer_type:
                    getAnswerType(),

                language:
                    languageSelect
                        ? languageSelect.value
                        : "English",

                length:
                    lengthSelect
                        ? lengthSelect.value
                        : "medium",

                note_style:
                    "Handwritten Study Notes"
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Could not generate answer."
            );
        }

        lastAnswer = String(
            data.answer || ""
        ).trim();

        if (!lastAnswer) {

            throw new Error(
                "AI returned an empty answer."
            );
        }

        displayAnswer(lastAnswer);

        createHandwrittenNotes(
            question,
            lastAnswer
        );

        setStatus("READY");

    } catch (error) {

        console.error(
            "Answer Pilot Error:",
            error
        );

        showAnswerError(
            error.message
        );

        showNotesError();

        setStatus("ERROR");

    } finally {

        setLoading(false);
    }
}

/* ============================================================
UI STATE
============================================================ */

function setLoading(loading) {

    if (!generateButton) {
        return;
    }

    generateButton.disabled = loading;

    if (loading) {

        generateButton.innerHTML =
            "Generating...";

    } else {

        generateButton.innerHTML =
            "<span>✦</span> Generate Answer";
    }
}

function setStatus(status) {

    if (answerStatus) {
        answerStatus.textContent = status;
    }
}

function showAnswerLoading() {

    if (!answerOutput) {
        return;
    }

    answerOutput.innerHTML =
        '<div class="empty-notes">' +
        '<div>✦</div>' +
        '<span>Generating your exam-ready answer...</span>' +
        '</div>';
}

function showNotesLoading() {

    if (!notesPreview) {
        return;
    }

    notesPreview.innerHTML =
        '<div class="empty-notes">' +
        '<div>✎</div>' +
        '<span>Preparing handwritten study notes...</span>' +
        '</div>';
}

function showAnswerError(message) {

    if (!answerOutput) {
        return;
    }

    answerOutput.innerHTML =
        '<div class="empty-notes">' +
        '<div>!</div>' +
        '<span>' +
        escapeHTML(
            message ||
            "Something went wrong."
        ) +
        '</span>' +
        '</div>';
}

function showNotesError() {

    if (!notesPreview) {
        return;
    }

    notesPreview.innerHTML =
        '<div class="empty-notes">' +
        '<div>!</div>' +
        '<span>Handwritten notes could not be created.</span>' +
        '</div>';
}

/* ============================================================
NORMAL ANSWER
============================================================ */

function displayAnswer(answer) {

    if (!answerOutput) {
        return;
    }

    answerOutput.innerHTML =
        '<div class="answer-content">' +
        formatAnswer(answer) +
        '</div>';
}

function formatAnswer(text) {

    const cleaned =
        cleanMarkdown(text);

    const lines =
        cleaned.split("\n");

    let html = "";
    let listOpen = false;

    function closeList() {

        if (listOpen) {
            html += "</ul>";
            listOpen = false;
        }
    }

    lines.forEach(function (rawLine) {

        const line =
            rawLine.trim();

        if (!line) {

            closeList();

            html +=
                '<div class="answer-space"></div>';

            return;
        }

        if (/^#{1,3}\s+/.test(line)) {

            closeList();

            html +=
                "<h2>" +
                formatInline(
                    removeHeadingMarks(line)
                ) +
                "</h2>";

            return;
        }

        const numbered =
            line.match(
                /^(\d+)[.)]\s*(.+)$/
            );

        if (numbered) {

            closeList();

            html +=
                '<div class="answer-point">' +

                '<span class="point-number">' +
                escapeHTML(
                    numbered[1]
                ) +
                ".</span> " +

                formatInline(
                    numbered[2]
                ) +

                "</div>";

            return;
        }

        const bullet =
            line.match(
                /^[-*•]\s*(.+)$/
            );

        if (bullet) {

            if (!listOpen) {

                html += "<ul>";

                listOpen = true;
            }

            html +=
                "<li>" +
                formatInline(
                    bullet[1]
                ) +
                "</li>";

            return;
        }

        closeList();

        html +=
            '<p class="answer-paragraph">' +
            formatInline(line) +
            "</p>";
    });

    closeList();

    return html;
}

/* ============================================================
MARKDOWN CLEANUP
============================================================ */

function cleanMarkdown(text) {

    if (!text) {
        return "";
    }

    let value =
        String(text)
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n");

    value =
        value.replace(
            /```[a-zA-Z0-9_-]*\s*/g,
            ""
        );

    value =
        value.replace(
            /```/g,
            ""
        );

    value =
        value.replace(
            /^---+\s*$/gm,
            ""
        );

    value =
        value.replace(
            /^\s*\\{2,3}/gm,
            ""
        );

    return value.trim();
}

function removeHeadingMarks(text) {

    return text
        .replace(/^###\s+/, "")
        .replace(/^##\s+/, "")
        .replace(/^#\s+/, "")
        .trim();
}

function formatInline(text) {

    let value =
        escapeHTML(text);

    value =
        value.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );

    value =
        value.replace(
            /__(.*?)__/g,
            "<strong>$1</strong>"
        );

    value =
        value.replace(
            /\*(.*?)\*/g,
            "<em>$1</em>"
        );

    value =
        value.replace(
            /_(.*?)_/g,
            "<em>$1</em>"
        );

    return value;
}

function escapeHTML(text) {

    const element =
        document.createElement("div");

    element.textContent =
        String(text);

    return element.innerHTML;
}

/* ============================================================
HANDWRITTEN NOTES
============================================================ */

function createHandwrittenNotes(
    question,
    answer
) {

    const cleanAnswer =
        cleanMarkdown(answer);

    const lines =
        cleanAnswer
            .split("\n")
            .map(function (line) {
                return line.trim();
            })
            .filter(function (line) {
                return line.length > 0;
            });

    notePages =
        splitIntoNaturalPages(
            question,
            lines
        );

    currentPage = 0;

    renderNotePage();

    updatePageControls();
}

/* ============================================================
NATURAL PAGE SPLITTING
============================================================ */

function splitIntoNaturalPages(
    question,
    lines
) {

    const pages = [];

    let currentPageLines = [];
    let currentCharacters = 0;

    const maxCharacters =
        getPageCharacterLimit();

    lines.forEach(function (line) {

        const lineLength =
            line.length;

        const isHeading =
            /^#{1,3}\s+/.test(line);

        const isNumbered =
            /^\d+[.)]\s+/.test(line);

        const extraSpace =
            isHeading || isNumbered
                ? 35
                : 0;

        const newSize =
            currentCharacters +
            lineLength +
            extraSpace;

        if (
            currentPageLines.length > 0 &&
            newSize > maxCharacters
        ) {

            pages.push({
                question: question,
                lines: currentPageLines
            });

            currentPageLines = [];

            currentCharacters = 0;
        }

        currentPageLines.push(line);

        currentCharacters +=
            lineLength +
            extraSpace;
    });

    if (currentPageLines.length > 0) {

        pages.push({
            question: question,
            lines: currentPageLines
        });
    }

    if (pages.length === 0) {

        pages.push({
            question: question,
            lines: [
                "No answer available."
            ]
        });
    }

    return pages;
}

function getPageCharacterLimit() {

    if (!lengthSelect) {
        return 1450;
    }

    if (
        lengthSelect.value === "short"
    ) {
        return 1050;
    }

    if (
        lengthSelect.value === "long"
    ) {
        return 1550;
    }

    return 1350;
}

/* ============================================================
RENDER CURRENT PAGE
============================================================ */

function renderNotePage() {

    if (!notesPreview) {
        return;
    }

    if (!notePages.length) {

        notesPreview.innerHTML =
            '<div class="empty-notes">' +
            '<div>✎</div>' +
            '<span>Your handwritten-style notes will appear here.</span>' +
            '</div>';

        updatePageControls();

        return;
    }

    const page =
        notePages[currentPage];

    let html = "";

    page.lines.forEach(function (line) {

        html +=
            renderNoteLine(line);
    });

    notesPreview.innerHTML =
        '<div class="note-page">' +

        '<div class="note-page-header">' +
        '<span>Answer Pilot — AI Study Notes</span>' +
        '<span>Page ' +
        (currentPage + 1) +
        '</span>' +
        '</div>' +

        '<div class="note-title">' +
        escapeHTML(page.question) +
        '</div>' +

        html +

        '<div class="note-page-footer">' +
        'Answer Pilot • Handwritten Study Notes' +
        '</div>' +

        '</div>';

    updatePageControls();
}

/* ============================================================
RENDER NOTE LINE
============================================================ */

function renderNoteLine(line) {

    if (
        /^#{1,3}\s+/.test(line)
    ) {

        return (
            '<h2>' +
            formatInline(
                removeHeadingMarks(line)
            ) +
            '</h2>'
        );
    }

    const numbered =
        line.match(
            /^(\d+)[.)]\s*(.+)$/
        );

    if (numbered) {

        return (
            '<p>' +
            '<strong>' +
            escapeHTML(numbered[1]) +
            '.</strong> ' +
            formatInline(
                numbered[2]
            ) +
            '</p>'
        );
    }

    const bullet =
        line.match(
            /^[-*•]\s*(.+)$/
        );

    if (bullet) {

        return (
            '<p>' +
            '• ' +
            formatInline(
                bullet[1]
            ) +
            '</p>'
        );
    }

    const specialHeading =
        normalizeSpecialHeading(line);

    if (specialHeading) {

        return (
            '<h3>' +
            escapeHTML(
                specialHeading
            ) +
            '</h3>'
        );
    }

    return (
        '<p>' +
        formatInline(line) +
        '</p>'
    );
}

/* ============================================================
SPECIAL HEADINGS
============================================================ */

function normalizeSpecialHeading(line) {

    const value =
        line
            .replace(/:$/, "")
            .trim();

    const lower =
        value.toLowerCase();

    const headings = {
        "definition": "Definition",
        "introduction": "Introduction",
        "key points": "Key Points",
        "important points": "Important Points",
        "examples": "Examples",
        "example": "Example",
        "advantages": "Advantages",
        "disadvantages": "Disadvantages",
        "applications": "Applications",
        "working": "Working",
        "process": "Process",
        "conclusion": "Conclusion",
        "labelled diagram": "Labelled Diagram",
        "labeled diagram": "Labelled Diagram"
    };

    return headings[lower] || "";
}

/* ============================================================
PAGE CONTROLS
============================================================ */

function updatePageControls() {

    if (pageCounter) {

        pageCounter.textContent =
            "Page " +
            (
                notePages.length
                    ? currentPage + 1
                    : 0
            ) +
            " / " +
            notePages.length;
    }

    if (previousPageButton) {

        previousPageButton.disabled =
            currentPage <= 0;
    }

    if (nextPageButton) {

        nextPageButton.disabled =
            currentPage >=
            notePages.length - 1;
    }
}

if (previousPageButton) {

    previousPageButton.addEventListener(
        "click",
        function () {

            if (currentPage > 0) {

                currentPage--;

                renderNotePage();
            }
        }
    );
}

if (nextPageButton) {

    nextPageButton.addEventListener(
        "click",
        function () {

            if (
                currentPage <
                notePages.length - 1
            ) {

                currentPage++;

                renderNotePage();
            }
        }
    );
}

/* ============================================================
COPY ANSWER
============================================================ */

if (copyAnswerButton) {

    copyAnswerButton.addEventListener(
        "click",
        async function () {

            if (!lastAnswer) {

                alert(
                    "Generate an answer first."
                );

                return;
            }

            try {

                await navigator.clipboard.writeText(
                    lastAnswer
                );

                const oldText =
                    copyAnswerButton.textContent;

                copyAnswerButton.textContent =
                    "✓ Copied";

                setTimeout(
                    function () {

                        copyAnswerButton.textContent =
                            oldText;

                    },
                    1500
                );

            } catch (error) {

                alert(
                    "Could not copy the answer."
                );
            }
        }
    );
}

/* ============================================================
REGENERATE
============================================================ */

if (regenerateButton) {

    regenerateButton.addEventListener(
        "click",
        function () {

            if (!lastQuestion) {

                alert(
                    "Generate an answer first."
                );

                return;
            }

            questionInput.value =
                lastQuestion;

            generateAnswer();
        }
    );
}

/* ============================================================
DOWNLOAD ANSWER
============================================================ */

if (downloadAnswerButton) {

    downloadAnswerButton.addEventListener(
        "click",
        function () {

            if (!lastAnswer) {

                alert(
                    "Generate an answer first."
                );

                return;
            }

            const content =
                "ANSWER PILOT\n\n" +
                "QUESTION:\n" +
                lastQuestion +
                "\n\n" +
                "ANSWER:\n" +
                lastAnswer;

            downloadFile(
                content,
                "AnswerPilot_Answer.txt",
                "text/plain"
            );
        }
    );
}

/* ============================================================
DOWNLOAD NOTES
============================================================ */

if (downloadNotesButton) {

    downloadNotesButton.addEventListener(
        "click",
        function () {

            if (!notePages.length) {

                alert(
                    "Generate an answer first."
                );

                return;
            }

            const html =
                buildPrintableNotes();

            downloadFile(
                html,
                "AnswerPilot_Handwritten_Notes.html",
                "text/html"
            );
        }
    );
}

/* ============================================================
PRINTABLE NOTES
============================================================ */

function buildPrintableNotes() {

    let pagesHTML = "";

    notePages.forEach(
        function (page, index) {

            let content = "";

            page.lines.forEach(
                function (line) {

                    content +=
                        renderPrintableLine(
                            line
                        );
                }
            );

            pagesHTML +=
                '<section class="print-page">' +

                '<header>' +

                '<strong>' +
                'Answer Pilot — AI Study Notes' +
                '</strong>' +

                '<span>' +
                'Page ' +
                (index + 1) +
                '</span>' +

                '</header>' +

                '<h1>' +
                escapeHTML(
                    page.question
                ) +
                '</h1>' +

                content +

                '<footer>' +
                'Answer Pilot • Handwritten Study Notes' +
                '</footer>' +

                '</section>';
        }
    );

    return (
        "<!DOCTYPE html>" +
        "<html>" +
        "<head>" +
        '<meta charset="UTF-8">' +
        "<title>Answer Pilot Notes</title>" +

        "<style>" +

        "body{" +
        "margin:0;" +
        "background:#ddd;" +
        'font-family:"Comic Sans MS","Segoe Print",cursive;' +
        "}" +

        ".print-page{" +
        "width:210mm;" +
        "min-height:297mm;" +
        "box-sizing:border-box;" +
        "margin:20px auto;" +
        "padding:22mm 18mm 20mm 25mm;" +
        "position:relative;" +
        "background:#fffdf5;" +
        "background-image:repeating-linear-gradient(to bottom,transparent 0,transparent 30px,#dce5ef 31px,#fffdf5 32px);" +
        "page-break-after:always;" +
        "}" +

        ".print-page:before{" +
        "content:'';" +
        "position:absolute;" +
        "left:18mm;" +
        "top:0;" +
        "bottom:0;" +
        "width:1px;" +
        "background:#df9696;" +
        "}" +

        ".print-page header{" +
        "display:flex;" +
        "justify-content:space-between;" +
        "font-size:12px;" +
        "margin-bottom:24px;" +
        "}" +

        ".print-page h1{" +
        "font-size:24px;" +
        "text-align:center;" +
        "color:#31558d;" +
        "margin-bottom:24px;" +
        "}" +

        ".print-page h2," +
        ".print-page h3{" +
        "color:#d32d87;" +
        "margin-top:16px;" +
        "margin-bottom:8px;" +
        "}" +

        ".print-page p{" +
        "font-size:14px;" +
        "line-height:1.95;" +
        "color:#263f6b;" +
        "margin:5px 0;" +
        "}" +

        ".print-page footer{" +
        "position:absolute;" +
        "left:0;" +
        "right:0;" +
        "bottom:12px;" +
        "text-align:center;" +
        "font-size:11px;" +
        "}" +

        "@media print{" +
        "body{background:white;}" +
        ".print-page{margin:0;}" +
        "}" +

        "</style>" +

        "</head>" +

        "<body>" +

        pagesHTML +

        "</body>" +

        "</html>"
    );
}

function renderPrintableLine(line) {

    if (/^#{1,3}\s+/.test(line)) {

        return (
            "<h2>" +
            formatInline(
                removeHeadingMarks(line)
            ) +
            "</h2>"
        );
    }

    const numbered =
        line.match(
            /^(\d+)[.)]\s*(.+)$/
        );

    if (numbered) {

        return (
            "<p><strong>" +
            escapeHTML(
                numbered[1]
            ) +
            ".</strong> " +
            formatInline(
                numbered[2]
            ) +
            "</p>"
        );
    }

    const bullet =
        line.match(
            /^[-*•]\s*(.+)$/
        );

    if (bullet) {

        return (
            "<p>• " +
            formatInline(
                bullet[1]
            ) +
            "</p>"
        );
    }

    const special =
        normalizeSpecialHeading(line);

    if (special) {

        return (
            "<h3>" +
            escapeHTML(special) +
            "</h3>"
        );
    }

    return (
        "<p>" +
        formatInline(line) +
        "</p>"
    );
}

/* ============================================================
FILE DOWNLOAD
============================================================ */

function downloadFile(
    content,
    filename,
    mimeType
) {

    const blob =
        new Blob(
            [content],
            {
                type:
                    mimeType +
                    ";charset=utf-8"
            }
        );

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(
        link
    );

    link.click();

    document.body.removeChild(
        link
    );

    URL.revokeObjectURL(
        url
    );
}

/* ============================================================
ENTER KEY
============================================================ */

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                generateAnswer();
            }
        }
    );
}

/* ============================================================
PDF UPLOAD
============================================================ */

if (fileInput) {

    fileInput.addEventListener(
        "change",
        async function () {

            const files =
                Array.from(
                    fileInput.files
                );

            for (
                const file of files
            ) {

                await uploadFile(
                    file
                );
            }

            fileInput.value = "";
        }
    );
}

/* ============================================================
UPLOAD PDF
============================================================ */

async function uploadFile(file) {

    if (
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        alert(
            "Only PDF files are supported."
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    try {

        const response =
            await fetch(
                "/upload",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Upload failed."
            );
        }

        uploadedFiles.push({

            name:
                data.filename ||
                file.name,

            size:
                file.size,

            chunks:
                data.chunks || 0
        });

        updateFileList();

    } catch (error) {

        console.error(
            "Upload Error:",
            error
        );

        alert(
            "Could not upload " +
            file.name +
            "\n\n" +
            error.message
        );
    }
}

/* ============================================================
FILE LIST
============================================================ */

function updateFileList() {

    if (!fileList) {
        return;
    }

    fileList.innerHTML = "";

    uploadedFiles.forEach(
        function (file, index) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "uploaded-file";

            item.innerHTML =
                '<div class="file-info">' +

                '<div class="file-icon">PDF</div>' +

                '<div>' +

                "<strong>" +
                escapeHTML(
                    file.name
                ) +
                "</strong>" +

                "<small>" +
                formatFileSize(
                    file.size
                ) +
                "</small>" +

                "</div>" +

                "</div>" +

                '<button type="button" class="remove-file" data-index="' +
                index +
                '">×</button>';

            fileList.appendChild(
                item
            );
        }
    );

    if (fileCount) {

        fileCount.textContent =
            uploadedFiles.length +
            (
                uploadedFiles.length === 1
                    ? " file"
                    : " files"
            );
    }

    document
        .querySelectorAll(
            ".remove-file"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const index =
                            Number(
                                button.getAttribute(
                                    "data-index"
                                )
                            );

                        uploadedFiles.splice(
                            index,
                            1
                        );

                        updateFileList();
                    }
                );
            }
        );
}

/* ============================================================
FILE SIZE
============================================================ */

function formatFileSize(bytes) {

    if (!bytes || bytes <= 0) {
        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];

    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );

    return (
        parseFloat(
            (
                bytes /
                Math.pow(
                    1024,
                    index
                )
            ).toFixed(1)
        ) +
        " " +
        units[index]
    );
}

/* ============================================================
INITIALIZE
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const active =
            document.querySelector(
                ".answer-type.active"
            );

        if (active) {

            selectedAnswerType =
                active.getAttribute(
                    "data-type"
                ) || "exam";

        } else if (
            answerTypeButtons.length > 0
        ) {

            answerTypeButtons[0]
                .classList
                .add("active");

            selectedAnswerType =
                answerTypeButtons[0]
                    .getAttribute(
                        "data-type"
                    ) || "exam";
        }

        updatePageControls();
    }
);