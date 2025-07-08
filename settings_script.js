let backend = null;
let radioDoNothing = null;
let radioStartServer = null;
let radioKeepLastState = null;

let radioExit = null;
let radioMinimizeToTray = null;

window.onload = function() {
    console.log("Window loaded, setting up WebChannel...");
    new QWebChannel(qt.webChannelTransport, function(channel) {
        console.log("WebChannel connected, backend ready");
        backend = channel.objects.backend;

        // When App Starts Radio Buttons
        radioDoNothing = document.getElementById('radioNothing');
        radioStartServer = document.getElementById('radioStartServer');
        radioKeepLastState = document.getElementById('radioKeepLastState');

        // When click close radio buttons
        radioExit = document.getElementById('radioExit');
        radioMinimizeToTray = document.getElementById('radioMinimizeToTray');

        document.getElementById('logs').innerHTML = "Logs : " + "";
        //backend.getKeepLastState() + " , " + backend.getAutoStart();

        backend.getKeepLastState(function(state) {
            //console.log("KeepLastState : "  + state);
            if(state == true){
                radioKeepLastState.checked = true;
                radioStartServer.checked = false;
                radioDoNothing.checked = false;
            }
        });

        backend.getAutoStart(function(state) {
            //console.log("KeepLastState : "  + state);
            if(state == true){
                radioKeepLastState.checked = false;
                radioStartServer.checked = true;
                radioDoNothing.checked = false;
            }
        });

        backend.getMinimizeToTray(function(state) {
            //console.log("KeepLastState : "  + state);
            if(state == true){
                radioMinimizeToTray.checked = true;
                radioExit.checked = false;
            }
        });
        


    });
};

function OnDoNothingRadioClick(){
    if(backend != null){
        backend.setAutoStart(false);
        backend.setKeepLastState(false);
    }
}

function OnStartServerRadioClick(){
    if(backend != null){
        backend.setAutoStart(true);
        backend.setKeepLastState(false);
    }
}

function OnKeepLastStateRadioClick(){
    if(backend != null){
        backend.setAutoStart(false);
        backend.setKeepLastState(true);
    }
}

function SetCloseBehaviour(state){
    if (typeof state === 'boolean') {
        if(backend != null){
            backend.setMinimizeToTray(state);
        }
    }
}

function SaveSetting(){
    if(backend != null){
        backend.saveSettings();
    }
}