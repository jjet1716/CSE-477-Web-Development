const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
                87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
                83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
                69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
                68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
                70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
                84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
                71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
                89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
                72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
                85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
                74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
                75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
                79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
                76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
                80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
                186:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav",
                'Awoken':"https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1"};

function main() {
    /** Handle Piano Hover Effect */
    var piano = document.getElementById("piano-container");

    function pianoHover(onHover, offHover) {
        piano.addEventListener('mouseenter', onHover);
        piano.addEventListener('mouseleave', offHover);
    }

    // add listeners to know when your hovering or not over the piano
    pianoHover(onHover => {
        piano.classList.add("visiting");
    }, offHover => {
        piano.classList.remove("visiting");
    });


    /** Process Key Events */
    var string_seq = "";

    var KeyDownHandler = function(e) {
        let end = onPianoKey(e, 'down');
        if (end) {

            // stop listening once awoken
            document.removeEventListener('keydown', KeyDownHandler);
            document.removeEventListener('keydown', KeyUpHandler);
        }
    };

    var KeyUpHandler = function(e) {
        onPianoKey(e, 'up');
    };

    document.addEventListener('keydown', KeyDownHandler);
    document.addEventListener('keyup', KeyUpHandler);

    function onPianoKey(keyEvent, type) {
        let key = String(keyEvent.key).toUpperCase();
        let pressed_key = "inner-";
        let audioObj;
        switch(key) {
            case 'A':
                pressed_key = pressed_key + 'A';
                audioObj = new Audio(sound[65]);
                break;
            case "S":
                pressed_key = pressed_key + 'S';
                audioObj = new Audio(sound[83]);
                break;
            case "D":
                pressed_key = pressed_key + 'D';
                audioObj = new Audio(sound[68]);
                break;
            case "F":
                pressed_key = pressed_key + 'F';
                audioObj = new Audio(sound[70]);
                break;
            case "G":
                pressed_key = pressed_key + 'G';
                audioObj = new Audio(sound[71]);
                break;
            case "H":
                pressed_key = pressed_key + 'H';
                audioObj = new Audio(sound[72]);
                break;
            case "J":
                pressed_key = pressed_key + 'J';
                audioObj = new Audio(sound[74]);
                break;
            case "K":
                pressed_key = pressed_key + 'K';
                audioObj = new Audio(sound[75]);
                break;
            case "L":
                pressed_key = pressed_key + 'L';
                audioObj = new Audio(sound[76]);
                break;
            case ";":
                pressed_key = pressed_key + 'semi';
                audioObj = new Audio(sound[186]);
                break;
            case "W":
                pressed_key = pressed_key + 'W';
                audioObj = new Audio(sound[87]);
                break;
            case "E":
                pressed_key = pressed_key + 'E';
                audioObj = new Audio(sound[69]);
                break;
            case "T":
                pressed_key = pressed_key + 'T';
                audioObj = new Audio(sound[84]);
                break;
            case "Y":
                pressed_key = pressed_key + 'Y';
                audioObj = new Audio(sound[89]);
                break;
            case "U":
                pressed_key = pressed_key + 'U';
                audioObj = new Audio(sound[85]);
                break;
            case "O":
                pressed_key = pressed_key + 'O';
                audioObj = new Audio(sound[79]);
                break;
            case "P":
                pressed_key = pressed_key + 'P';
                audioObj = new Audio(sound[80]);
                break;
            default:
                return;
        }

        // prevent user from 'holding' notes 
        if (keyEvent.repeat) {
            document.getElementById(pressed_key).classList.remove("pressed");
        }

        // if pressed down, play audio of key
        else if (type === 'down') {
            document.getElementById(pressed_key).classList.add("pressed");
            string_seq = string_seq + pressed_key.slice(-1);
            string_seq = string_seq.substring(string_seq.length - 8);
            audioObj.play();
        }

        // if pressed up, unpress the key by removing 'pressed' class
        else if (type === 'up') {
            document.getElementById(pressed_key).classList.remove("pressed");
        }


        // when last sequence of 8 keys pressed == 'WEESEEYOU', trigger awoken state
        if (string_seq === 'WESEEYOU') {
            string_seq = "";
            document.getElementById("piano-container").classList.add("awoken");
            document.getElementById("piano-header").innerHTML = "I have Awoken";
            audioObj = new Audio(sound['Awoken']);
            audioObj.play();
            return true;
        }
    }
}

window.onload = main;
