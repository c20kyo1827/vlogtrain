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
\n\
    // A testbench\n\
    reg[1:0] in=0;\n\
    initial begin\n\
        #10 in <= 'b00;\n\
        #10 in <= 'b01;\n\
        #20 in <= 'b10;\n\
        #20 in <= 'b11;\n\
        $display (\"Hello world! The current time is (%0d ps)\", $time);\n\
        #50 $finish;            // Quit the simulation\n\
    end\n\
\n\
    initial\n\
    begin\n\
        $dumpfile(\"top_module.vcd\");\n\
        $dumpvars(0, top_module);\n\
    end\n\
    invert inst1 ( .in(in) );   // Sub-modules work too.\n\
\n\
endmodule\n\
\n\
module invert(input[1:0] in, output[1:0] out);\n\
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
            const waveBox = document.querySelector(".code-waveform");
            console.log(msgBox);
            msgBox.innerText = json["info"];
            console.log(json["waveform"]);
            const imagePath = json["waveform"].replace(/\\/g, '/');
            console.log(imagePath);
            const linkElement = document.createElement('a');
            linkElement.classList.add("info-href");
            linkElement.innerText = "Your waveform";
            linkElement.href = imagePath;  // 设置超链接的目标 URL
            console.log(linkElement);
            waveBox.appendChild(linkElement);
            // waveBox.style.backgroundImage = "url("+imagePath+")";
        }
    });
}