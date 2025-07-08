let backend = null;
let toggleServerButton = null;

window.onload = function() {
    console.log("Window loaded, setting up WebChannel...");
    new QWebChannel(qt.webChannelTransport, function(channel) {
        console.log("WebChannel connected, backend ready");
        backend = channel.objects.backend;

        serverAddressInput = document.getElementById("serverAddress");
        serverPortInput = document.getElementById("serverPort");

        
        

        toggleServerButton = document.getElementById("ToggleServer");
        toggleServerButton.addEventListener("click", function(){
            
            endpointList = document.getElementById("endpointList");
            encodingList = document.getElementById('encodingList');

            backend.setServerIp(serverAddressInput.value);
            backend.setServerPort(serverPortInput.value);
            
            if (!isNaN(endpointList.value)) {
               backend.setEndpoint(parseInt(endpointList.value)); 
            }

            backend.setEncoding(encodingList.value)
            
            ToggleServer();
        })

        resetServerButton = document.getElementById("ResetServer");
        resetServerButton.addEventListener("click", function(){
            backend.resetServer();
        });

        backend.serverStatusChanged.connect(function(status){
            if(status == true){
                toggleServerButton.innerHTML= "Stop Server";
            }else{
                toggleServerButton.innerHTML= "Start Server";
            }
        });

        serverOutput = document.getElementById("serverOutput");

        backend.serverlogOutput.connect(function(msg){
            // "&#13;&#10;" means new line
            serverOutput.innerHTML += msg + "&#13;&#10;";
            serverOutput.scrollTop = serverOutput.scrollHeight;
        });


        backend.get_local_ipv4_address(function(ip){
            serverAddressInput.value = ip;
        });

        // Get Audio Endpoints
        backend.getEndpointList(function(endpoints) {
            console.log("Received endpoints:", endpoints);
        
            
            let select = document.getElementById("endpointList");
            select.innerHTML = ""; // clear existing

            endpoints.forEach(ep => {
                const option = document.createElement("option");
                option.value = ep.id;
                option.textContent = ep.name;

                if(ep.active){
                    option.classList.add("active");
                }
                
                select.appendChild(option);
            });
        });
    
        // Get available encoding Encoding 
        backend.getEncodingList(function(encoding){
            let select = document.getElementById("encodingList");
            select.innerHTML = "";

            encoding.forEach(en => {
                let option = document.createElement("option");
                option.value = en.key;
                option.textContent = en.description;

                select.appendChild(option);
            });
        });

        // Get AudioEndpoint
        backend.getEndpoint(function(endpoint){
            let select = document.getElementById("endpointList");
            Array.from(select.options).forEach(function(option_element) {
                if(option_element.value == endpoint){
                    option_element.selected = true;
                    option_element.classList.add("active");
                }
                else{
                    option_element.selected = false;
                    option_element.classList.remove("active");
                }
            });
        });

        // Get AudioEncoding
        backend.getEncoding(function(encoding){
            let select = document.getElementById("encodingList");
            Array.from(select.options).forEach(function(option_element) {
                if(option_element.value == encoding){
                    option_element.selected = true;
                    option_element.classList.add("active");
                }
                else{
                    option_element.selected = false;
                    option_element.classList.remove("active");
                }
            });
        });
        
    });
};

function OnEndpointChange(){
    let select = document.getElementById("endpointList");
    let encodingList = document.getElementById("encodingList");
    
    if(backend != null){

        if (!isNaN(select.value)) {
            backend.setEndpoint(parseInt(select.value)); 
        }

        backend.setEncoding(encodingList.value)
    }
    

    const options = select.options;
    const encoding_options = encodingList.options;

    for (let i = 0; i < options.length; i++) {
        const optionValue = options[i].value; // Get the value of the option
        const optionText = options[i].text;   // Get the display text of the option

        if (optionValue == select.value){
            options[i].classList.add("active");
        }
        else{
            options[i].classList.remove("active");
        }

        //console.log(`Option ${i}: Value = ${optionValue}, Text = ${optionText}`);
    }

    for (let i = 0; i < encoding_options.length; i++) {
        const optionValue = encoding_options[i].value; // Get the value of the option
        const optionText = encoding_options[i].text;   // Get the display text of the option

        if (optionValue == encodingList.value){
            encoding_options[i].classList.add("active");
        }
        else{
            encoding_options[i].classList.remove("active");
        }
    }

    backend.resetServer();
}

function ToggleServer(){
    if(backend != null){

        //backend.isServerRunning(function(status) {
            
        //});
        
        backend.toggleServer();

    }
}