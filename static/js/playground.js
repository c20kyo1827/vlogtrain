// Wrapping namespace
let playgroundNamespace = {};

window.onload = async function playgroundLoading(){
    playgroundNamespace.initialization();
}

playgroundNamespace.initialization = function initialization(){
    const myTextarea = document.querySelector(".code-editor");

    const myCodeMirror = CodeMirror.fromTextArea(myTextarea, {
        lineNumbers: true,
        mode: "verilog",
        theme: "3024-day"
    });
}