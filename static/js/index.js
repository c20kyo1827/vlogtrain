let indexNamespace = {};

// Main
window.onload = async function loading(){
    indexNamespace.addElementListener();
}

indexNamespace.addElementListener = function addElementListener(){
    const btn = document.getElementById("submit");
    btn.addEventListener("click", async () => {
        const code = document.getElementById("code").value;
        console.log(code);
        const data ={
            "code" : code
        };

        let url = "/api/sendVerilog";
        let response = 
        await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        let json = await response.json();
        console.log(json);
        if("ok" in json){
            const msgBox = document.getElementById("result");
            console.log(msgBox);
            msgBox.innerText = json["info"];
        }
    });
}