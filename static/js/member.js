// Wrapping namespace
let memberNamespace = {};

// Main
window.onload = async function bookLoading(){
    await memberNamespace.initialization();
    memberNamespace.addElementListener();
}

memberNamespace.initialization = async function initialization(){
    // Check authorization => return
    let loginCheck = false;
    await baseNamespace.checkSignState()
    .then((isLogin) => {
        loginCheck = isLogin
    })
    if(!loginCheck)
        window.location.href = "/";
    else{
        // User
        await memberNamespace.createMemberInfo();
    }
}

memberNamespace.addElementListener = function addElementListener(){
    ;
}

memberNamespace.createMemberInfo = async function createMemberInfo(){
    await baseNamespace.getAuthorization()
    .then((memberInfo) => {
        console.log(memberInfo);
        const id = document.querySelector("#id");
        const name = document.querySelector("#name");
        const email = document.querySelector("#email");
        const solved = document.querySelector("#solved");
        id.innerText = memberInfo["data"]["id"];
        name.innerText = memberInfo["data"]["name"];
        email.innerText = memberInfo["data"]["email"];
        solved.innerText = memberInfo["data"]["solved_problem"];
    })
}