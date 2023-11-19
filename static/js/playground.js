// Wrapping namespace
let playgroundNamespace = {};
let myCodeMirrorEditor;

window.onload = async function playgroundLoading(){
    playgroundNamespace.initialization();
    playgroundNamespace.addElementListener();
}

playgroundNamespace.initialization = function initialization(){
    const myTextarea = document.querySelector(".code-editor");

    myCodeMirrorEditor = CodeMirror.fromTextArea(myTextarea, {
        lineNumbers: true,
        mode: "verilog",
        theme: "3024-day"
    });

    myCodeMirrorEditor.getDoc().setValue(
"module top_module ();\n\
    reg clk=0;\n\
    always #5 clk = ~clk;  // Create clock with period=10\n\
\n\
    // A testbench\n\
    reg in=0;\n\
    initial begin\n\
        #10 in <= 1;\n\
        #10 in <= 0;\n\
        #20 in <= 1;\n\
        #20 in <= 0;\n\
        $display (\"Hello world! The current time is (%0d ps)\", $time);\n\
        #50 $finish;            // Quit the simulation\n\
    end\n\
\n\
    invert inst1 ( .in(in) );   // Sub-modules work too.\n\
\n\
endmodule\n\
\n\
module invert(input in, output out);\n\
    assign out = ~in;\n\
endmodule"
    );
}

playgroundNamespace.addElementListener = function addElementListener(){
    
    const btn = document.getElementById("submit");
    btn.addEventListener("click", async () => {
        const code = myCodeMirrorEditor.getValue()
        console.log(code);
        const currentDate = new Date();
        const fileName = currentDate.toISOString().replace(/[-T:.Z]/g, "_") + "playground.v";
        const data ={
            "fileName" : fileName,
            "code" : code
        };

        const url = "/api/runIverilog";
        let response = 
            await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
        let json = await response.json();
        if("ok" in json){
            const msgBox = document.querySelector(".code-result");
            console.log(msgBox);
            msgBox.innerText = json["info"];
        }
    });
}