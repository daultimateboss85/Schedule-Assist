async function myFetch(endpoint, method="GET",body,  content_type=null){

    let token = localStorage.getItem("token");

    if (token==null || token=="undefined"){
        let result = await fetch(endpoint, {
            method: method, 
            body: body
        })
        .then(async res=> {return [await res.json(), res.status]});

        return result;
    }


    else{
    /* allows for me to get request result */
    if(content_type){
        let result = await fetch(endpoint, {
            method: method,
            headers:{
                Authorization: `Bearer ${localStorage.getItem("token")}`,
                "Content-Type": content_type

            },
            body: body})
            .then(async res => {return [await res.json(), res.status] })
            
        return result;}
    else{
        let result = await fetch(endpoint, {
            method: method,
            headers:{
                Authorization: `Bearer ${localStorage.getItem("token")}`,
    
            },
            body: body})
            .then(async res => {return [await res.json(), res.status] } )
            
        return result;
    }}
    
}


/**
 * This function is true if status_code is 2xx
 * @param {number} status_code
 * @returns {boolean}
 *  */  

function eval_status_code(status_code){
    return Math.floor(status_code / 100) == 2;
}

function flash_message(message, status_code){
    /* Function handling display of messages */
    let container = document.createElement("div");
    container.innerHTML += `${message}`;

    let message_class = Number((status_code / 100).toFixed(0));
    let type;
    if ( message_class == 2){
        type = "success";
    }else{
        type = "failure";
    }

    container.classList.add("message", type, "disappear", "long");
    document.body.append(container);
}

export {myFetch, eval_status_code, flash_message}