
const keys = document.querySelectorAll('.keyboard-row button');
var boardRows = document.querySelectorAll('.board-row');
var messages = document.querySelector('#message-container')
var wordLen = boardRows.length;
var currentRow = 0;
var currentCol = 0;
var currentWord = "";
var timer;
var totalTimeInSeconds = 0;
var gameStarted = false;


if (document.querySelector('#instructions-container').getAttribute('show-instructions') == "False") {
    if (!gameStarted) {
        StartGame();
    }
}

function closeInstructions() {
    document.querySelector('#instructions-container').setAttribute('show-instructions', 'False');
    if (!gameStarted) {
        StartGame();
    }
}

function StartGame() {
    keys.forEach( (key) => {
        key.addEventListener("click", handleKeyMouse);
    });
    document.addEventListener('keydown', handleKeyPress);
    StartTimer();
    gameStarted = true;
}

function StartTimer() {
    timer = setInterval(countUp, 1000);
    var timerEle = document.getElementById("timer");

    function addZeroPadding(num) {
        if (num <= 9) {
            return String("0" + num);
        }
        return String(num);
    }

    function countUp() {
        ++totalTimeInSeconds;
        var hour = addZeroPadding(Math.floor(totalTimeInSeconds / 3600));
        var minute = addZeroPadding(Math.floor((totalTimeInSeconds - hour * 3600) / 60));
        var seconds = addZeroPadding(totalTimeInSeconds - (hour * 3600 + minute * 60));

        timerEle.innerHTML = hour + ':' + minute + ':' + seconds;
    }
}

function EndGame(won) {
    keys.forEach( (key) => {
        key.removeEventListener("click", handleKeyMouse);
    });
    document.removeEventListener('keydown', handleKeyPress);

    if (won) {
        addMessage('You Won!');
    } else {
        addMessage('Better luck next time...');
    }
    EndTimer();
    AddToLeaderboard(won);
}

function EndTimer() {
    clearInterval(timer);
}

function handleKeyMouse(e) {
    let pressedKey = e.target.getAttribute('data-key');
    if (pressedKey) {
        if (pressedKey === "BACK") {
            removeLetter();
        } 

        else if (pressedKey === "ENTER") {
            validateWord();
        } 
    
        else {
            addLetter(pressedKey);
        }
    }
}

function handleKeyPress(e) {
    let pressedKey = String(e.key).toUpperCase();
    if (pressedKey === "BACKSPACE") {
        removeLetter(pressedKey);
    } 

    else if (pressedKey === "ENTER") {
        validateWord();
    }

    else if (pressedKey.length === 1 && pressedKey.match(/[A-Z]/i)) {
        addLetter(pressedKey);
    } 
}

function addLetter(letter) {
    if (currentCol <= wordLen-1) {
        let tile = boardRows[currentRow].querySelectorAll('.board-tile')[currentCol];
        tile.textContent = letter;
        tile.setAttribute('data-state', 'tbd');

        currentWord += letter;

        currentCol++;
    }
}

function removeLetter() {
    if (currentCol > 0) {
        let tile = boardRows[currentRow].querySelectorAll('.board-tile')[currentCol-1];
        tile.textContent = "";
        tile.setAttribute('data-state', 'empty');

        currentWord = currentWord.slice(0, -1);

        currentCol--;
    }
}

function addMessage(text, lifetime=-1) {
    const newMessage = document.createElement('div');
    newMessage.setAttribute('class', 'message');
    const textNode = document.createTextNode(text);
    newMessage.appendChild(textNode);
    messages.appendChild(newMessage);

    if (lifetime != -1) {
        setTimeout( () => {
            messages.removeChild(newMessage);
        }, lifetime);
    }
}

function validateWord() {
    if (currentCol == wordLen) {
        console.log("word being validated: " + currentWord);

        // send word to server to be validated in backend
        jQuery.ajax({
            url: "/wordle/validateWord",
            data: {'word' : currentWord},
            type: "POST",
            success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                if (returned_data['success'] != 1) {
                    if (messages.children.length < 3) {
                        addMessage('Not in word list', 1500);
                    }
                } else {
                    advanceRow(returned_data);
                }
            }
        });
    } 
}

function advanceRow(word_data) {
    console.log('handling data: ');
    console.log(word_data);
    let tiles = boardRows[currentRow].querySelectorAll('.board-tile');
    let correct = true;
    for (let i=0; i<wordLen; i++) {
        let tile = tiles[i];
        let state = word_data[i];
        tile.setAttribute('data-state', state);

        if (state != 'correct') {
            correct = false;
        }
    }

    if (correct) {
        EndGame(true);
    } else {
        currentCol = 0;
        currentWord = "";
        currentRow++;

        if (currentRow == wordLen) {
            EndGame(false);
        }
    }
}

function AddToLeaderboard(won) {
    // add time to the leaderboard
    jQuery.ajax({
        url: "/wordle/addToLeaderboard",
        data: {'seconds' : totalTimeInSeconds, 'completed' : String(won)},
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            if (returned_data['success'] != 1) {
                setTimeout( () => {
                    addMessage('Score not added to Leaderboard - one try per day!');
                }, 1000);
                
            }
            setTimeout( () => {
                window.location.href = "/wordle/leaderboard";
            }, 2500);
        }
    });
}
