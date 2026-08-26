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

const answerTypeButtons = document.querySelectorAll(".answer-type");

let lastQuestion = "";
let lastAnswer = "";
let selectedAnswerType = "exam";

let notePages = [];
let currentPage = 0;

let uploadedFiles = [];


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


/* ============================================================
   GET ANSWER TYPE
============================================================ */

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
   GENERATE ANSWER
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

    if (generateButton) {
        generateButton.disabled = true;
        generateButton.innerHTML = "Generating...";
    }

    if (answerStatus) {
        answerStatus.textContent = "GENERATING";
    }

    if (answerOutput) {
        answerOutput.innerHTML =
            '<div class="empty-notes">' +
            '<div class="loading-spinner"></div>' +
            '<span>Creating your answer...</span>' +
            '</div>';
    }

    if (notesPreview) {
        notesPreview.innerHTML =
            '<div class="empty-notes">' +
            '<div>✎</div>' +
            '<span>Preparing handwritten-style notes...</span>' +
            '</div>';
    }

    try {

        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                answer_type: getAnswerType(),
                language: languageSelect
                    ? languageSelect.value
                    : "English",
                note_style: "Handwritten Study Notes"
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Could not generate answer."
            );
        }

        lastAnswer = data.answer || "";

        if (!lastAnswer) {
            throw new Error("AI returned an empty answer.");
        }

        displayAnswer(lastAnswer);

        createHandwrittenNotes(
            question,
            lastAnswer
        );

        if (answerStatus) {
            answerStatus.textContent = "READY";
        }

    } catch (error) {

        console.error("Answer Pilot Error:", error);

        if (answerStatus) {
            answerStatus.textContent = "ERROR";
        }

        if (answerOutput) {
            answerOutput.innerHTML =
                '<div class="error-answer">' +
                '<h3>Unable to generate answer</h3>' +
                '<p>' +
                escapeHTML(error.message) +
                '</p>' +
                '</div>';
        }

        if (notesPreview) {
            notesPreview.innerHTML =
                '<div class="empty-notes">' +
                '<div>!</div>' +
                '<span>Notes could not be generated.</span>' +
                '</div>';
        }

    } finally {

        if (generateButton) {
            generateButton.disabled = false;
            generateButton.innerHTML =
                '<span>✦</span> Generate Answer';
        }
    }
}


/* ============================================================
   DISPLAY ANSWER
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


/* ============================================================
   FORMAT ANSWER
============================================================ */

function formatAnswer(text) {

    const lines = text
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .split("\n");

    let html = "";
    let listOpen = false;

    function closeList() {

        if (listOpen) {
            html += "</ul>";
            listOpen = false;
        }
    }

    lines.forEach(function (line) {

        line = line.trim();

        if (!line) {
            closeList();
            html += '<div class="answer-space"></div>';
            return;
        }

        if (line.indexOf("### ") === 0) {

            closeList();

            html +=
                "<h3>" +
                formatInlineText(line.substring(4)) +
                "</h3>";

            return;
        }

        if (line.indexOf("## ") === 0) {

            closeList();

            html +=
                "<h2>" +
                formatInlineText(line.substring(3)) +
                "</h2>";

            return;
        }

        if (line.indexOf("# ") === 0) {

            closeList();

            html +=
                "<h1>" +
                formatInlineText(line.substring(2)) +
                "</h1>";

            return;
        }

        const numbered =
            line.match(/^(\d+)[.)]\s*(.*)$/);

        if (numbered) {

            closeList();

            html +=
                '<div class="answer-point">' +
                '<span class="point-number">' +
                escapeHTML(numbered[1]) +
                '.</span>' +
                '<span>' +
                formatInlineText(numbered[2]) +
                '</span>' +
                '</div>';

            return;
        }

        const bullet =
            line.match(/^[-*•]\s+(.*)$/);

        if (bullet) {

            if (!listOpen) {
                html += "<ul>";
                listOpen = true;
            }

            html +=
                "<li>" +
                formatInlineText(bullet[1]) +
                "</li>";

            return;
        }

        closeList();

        html +=
            '<p class="answer-paragraph">' +
            formatInlineText(line) +
            '</p>';
    });

    closeList();

    return html;
}


/* ============================================================
   INLINE TEXT
============================================================ */

function formatInlineText(text) {

    let safeText = escapeHTML(text);

    safeText = safeText.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    safeText = safeText.replace(
        /\*(.*?)\*/g,
        "<em>$1</em>"
    );

    return safeText;
}


/* ============================================================
   ESCAPE HTML
============================================================ */

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = String(text);

    return div.innerHTML;
}


/* ============================================================
   CREATE HANDWRITTEN NOTES
============================================================ */

function createHandwrittenNotes(question, answer) {

    const lines = answer
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .split("\n")
        .map(function (line) {
            return line.trim();
        })
        .filter(function (line) {
            return line.length > 0;
        });

    let linesPerPage = 16;

    if (lengthSelect) {

        if (lengthSelect.value === "short") {
            linesPerPage = 12;
        }

        if (lengthSelect.value === "long") {
            linesPerPage = 20;
        }
    }

    notePages = [];

    let currentLines = [];

    lines.forEach(function (line) {

        currentLines.push(line);

        if (currentLines.length >= linesPerPage) {

            notePages.push({
                question: question,
                lines: currentLines
            });

            currentLines = [];
        }
    });

    if (currentLines.length > 0) {

        notePages.push({
            question: question,
            lines: currentLines
        });
    }

    if (notePages.length === 0) {

        notePages.push({
            question: question,
            lines: [answer]
        });
    }

    currentPage = 0;

    renderNotePage();
}


/* ============================================================
   RENDER NOTE PAGE
============================================================ */

function renderNotePage() {

    if (!notesPreview) {
        return;
    }

    if (notePages.length === 0) {

        notesPreview.innerHTML =
            '<div class="empty-notes">' +
            '<div>✎</div>' +
            '<span>Your handwritten-style notes will appear here.</span>' +
            '</div>';

        updatePageControls();

        return;
    }

    const page = notePages[currentPage];

    let content = "";

    page.lines.forEach(function (line) {

        const isNumber =
            /^\d+[.)]\s*/.test(line);

        const isBullet =
            /^[-*•]\s+/.test(line);

        if (isNumber) {

            content +=
                '<div class="note-line note-heading">' +
                formatInlineText(line) +
                '</div>';

        } else if (isBullet) {

            content +=
                '<div class="note-line note-bullet">' +
                "• " +
                formatInlineText(
                    line.replace(/^[-*•]\s+/, "")
                ) +
                '</div>';

        } else {

            content +=
                '<div class="note-line">' +
                formatInlineText(line) +
                '</div>';
        }
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

        '<div class="note-paper">' +
        content +
        '</div>' +

        '<div class="note-page-footer">' +
        'Answer Pilot • Handwritten Study Notes' +
        '</div>' +

        '</div>';

    updatePageControls();
}


/* ============================================================
   PAGE CONTROLS
============================================================ */

function updatePageControls() {

    if (pageCounter) {

        if (notePages.length === 0) {

            pageCounter.textContent =
                "Page 0 / 0";

        } else {

            pageCounter.textContent =
                "Page " +
                (currentPage + 1) +
                " / " +
                notePages.length;
        }
    }

    if (previousPageButton) {

        previousPageButton.disabled =
            currentPage <= 0;
    }

    if (nextPageButton) {

        nextPageButton.disabled =
            currentPage >= notePages.length - 1;
    }
}


/* ============================================================
   PREVIOUS PAGE
============================================================ */

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


/* ============================================================
   NEXT PAGE
============================================================ */

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

                alert("Generate an answer first.");

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

                setTimeout(function () {

                    copyAnswerButton.textContent =
                        oldText;

                }, 1500);

            } catch (error) {

                alert("Could not copy the answer.");
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

                alert("Generate an answer first.");

                return;
            }

            if (questionInput) {
                questionInput.value =
                    lastQuestion;
            }

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

                alert("Generate an answer first.");

                return;
            }

            const text =
                "Answer Pilot\n\n" +
                "Question:\n" +
                lastQuestion +
                "\n\n" +
                "Answer:\n" +
                lastAnswer;

            downloadFile(
                text,
                "AnswerPilot_Answer.txt",
                "text/plain"
            );
        }
    );
}


/* ============================================================
   DOWNLOAD HANDWRITTEN NOTES
============================================================ */

if (downloadNotesButton) {

    downloadNotesButton.addEventListener(
        "click",
        function () {

            if (notePages.length === 0) {

                alert("Generate an answer first.");

                return;
            }

            let html = "";

            notePages.forEach(
                function (page, index) {

                    let linesHTML = "";

                    page.lines.forEach(
                        function (line) {

                            linesHTML +=
                                '<div class="line">' +
                                formatInlineText(line) +
                                '</div>';
                        }
                    );

                    html +=
                        '<section class="page">' +

                        '<header>' +
                        '<strong>Answer Pilot — AI Study Notes</strong>' +
                        '<span>Page ' +
                        (index + 1) +
                        '</span>' +
                        '</header>' +

                        '<h1>' +
                        escapeHTML(page.question) +
                        '</h1>' +

                        linesHTML +

                        '<footer>' +
                        'Answer Pilot • Handwritten Study Notes' +
                        '</footer>' +

                        '</section>';
                }
            );

            const fullHTML =
                '<!DOCTYPE html>' +
                '<html>' +
                '<head>' +

                '<meta charset="UTF-8">' +

                '<title>Answer Pilot Notes</title>' +

                '<style>' +

                'body {' +
                'margin: 0;' +
                'background: #dddddd;' +
                'font-family: "Comic Sans MS", cursive;' +
                '}' +

                '.page {' +
                'width: 210mm;' +
                'min-height: 297mm;' +
                'margin: 20px auto;' +
                'padding: 25mm;' +
                'box-sizing: border-box;' +
                'background: white;' +
                'background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 31px, #d7e6f5 32px);' +
                '}' +

                'header {' +
                'display: flex;' +
                'justify-content: space-between;' +
                'margin-bottom: 30px;' +
                '}' +

                'h1 {' +
                'font-size: 26px;' +
                'margin-bottom: 30px;' +
                '}' +

                '.line {' +
                'font-size: 18px;' +
                'line-height: 32px;' +
                'min-height: 32px;' +
                '}' +

                'footer {' +
                'margin-top: 40px;' +
                'text-align: center;' +
                'font-size: 13px;' +
                '}' +

                '@media print {' +
                'body { background: white; }' +
                '.page { margin: 0; page-break-after: always; }' +
                '}' +

                '</style>' +

                '</head>' +

                '<body>' +
                html +
                '</body>' +

                '</html>';

            downloadFile(
                fullHTML,
                "AnswerPilot_Handwritten_Notes.html",
                "text/html"
            );
        }
    );
}


/* ============================================================
   DOWNLOAD FILE
============================================================ */

function downloadFile(
    content,
    filename,
    type
) {

    const blob =
        new Blob(
            [content],
            { type: type + ";charset=utf-8" }
        );

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);
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
   GENERATE BUTTON
============================================================ */

if (generateButton) {

    generateButton.addEventListener(
        "click",
        generateAnswer
    );
}


/* ============================================================
   FILE UPLOAD
============================================================ */

if (fileInput) {

    fileInput.addEventListener(
        "change",
        async function () {

            const files =
                Array.from(fileInput.files);

            for (const file of files) {

                await uploadFile(file);
            }

            fileInput.value = "";
        }
    );
}


/* ============================================================
   UPLOAD FILE
============================================================ */

async function uploadFile(file) {

    if (
        !file.name.toLowerCase().endsWith(".pdf")
    ) {

        alert(
            file.name +
            ": Only PDF files are supported."
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

        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Upload failed."
            );
        }

        uploadedFiles.push({
            name: data.filename || file.name,
            size: file.size,
            chunks: data.chunks || 0
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
   UPDATE FILE LIST
============================================================ */

function updateFileList() {

    if (!fileList) {
        return;
    }

    fileList.innerHTML = "";

    uploadedFiles.forEach(
        function (file, index) {

            const item =
                document.createElement("div");

            item.className =
                "uploaded-file";

            item.innerHTML =
                '<div class="file-info">' +

                '<div class="file-icon">PDF</div>' +

                '<div>' +

                '<strong>' +
                escapeHTML(file.name) +
                '</strong>' +

                '<small>' +
                formatFileSize(file.size) +
                '</small>' +

                '</div>' +

                '</div>' +

                '<button type="button" class="remove-file" data-index="' +
                index +
                '">×</button>';

            fileList.appendChild(item);
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

    const removeButtons =
        document.querySelectorAll(".remove-file");

    removeButtons.forEach(
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
                Math.pow(1024, index)
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

        const activeButton =
            document.querySelector(
                ".answer-type.active"
            );

        if (activeButton) {

            selectedAnswerType =
                activeButton.getAttribute(
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