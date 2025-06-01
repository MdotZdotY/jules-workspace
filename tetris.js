// 1. Setup Canvas and Context
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');

const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 20; // Size of each block in pixels

// Adjust canvas size based on constants
canvas.width = COLS * BLOCK_SIZE;
canvas.height = ROWS * BLOCK_SIZE;

// 2. Define Tetrominoes
const TETROMINOES = {
    'I': {
        shape: [
            [0,0,0,0],
            [1,1,1,1],
            [0,0,0,0],
            [0,0,0,0]
        ],
        color: 'cyan'
    },
    'L': {
        shape: [
            [0,1,0],
            [0,1,0],
            [0,1,1]
        ],
        color: 'orange'
    },
    'J': {
        shape: [
            [0,1,0],
            [0,1,0],
            [1,1,0]
        ],
        color: 'blue'
    },
    'T': {
        shape: [
            [0,0,0],
            [1,1,1],
            [0,1,0]
        ],
        color: 'purple'
    },
    'O': {
        shape: [
            [1,1],
            [1,1]
        ],
        color: 'yellow'
    },
    'S': {
        shape: [
            [0,1,1],
            [1,1,0],
            [0,0,0]
        ],
        color: 'green'
    },
    'Z': {
        shape: [
            [1,1,0],
            [0,1,1],
            [0,0,0]
        ],
        color: 'red'
    }
};

const PIECES = ['I', 'L', 'J', 'T', 'O', 'S', 'Z']; // For random selection

// 3. Game Board Representation
let board = [];
function initBoard() {
    for (let r = 0; r < ROWS; r++) {
        board[r] = [];
        for (let c = 0; c < COLS; c++) {
            board[r][c] = 0; // 0 represents an empty cell
        }
    }
}

// 4. Active Piece
let activePiece = {
    x: 0,
    y: 0,
    shape: null,
    color: ''
};

function newPiece() {
    const randomPieceType = PIECES[Math.floor(Math.random() * PIECES.length)];
    const piece = TETROMINOES[randomPieceType];
    activePiece.shape = piece.shape;
    activePiece.color = piece.color;
    activePiece.x = Math.floor(COLS / 2) - Math.ceil(activePiece.shape[0].length / 2);
    activePiece.y = 0;

    // Game over condition (will be refined later with isValidMove)
    // if (collision()) { // Old collision check
    //     handleGameOver();
    // }
}

// 2. Collision Detection (Refined)
function isValidMove(testX, testY, testShape) {
    if (!testShape) return false;
    for (let y = 0; y < testShape.length; y++) {
        for (let x = 0; x < testShape[y].length; x++) {
            if (testShape[y][x] > 0) { // If it's part of the piece
                let newX = testX + x;
                let newY = testY + y;

                // Boundary checks
                if (newX < 0 || newX >= COLS || newY >= ROWS) {
                    return false; // Out of bounds
                }
                // Check board for landed pieces (only if newY is non-negative)
                if (newY < 0) continue; // Pieces can start above the visible board, this is fine for y but not for collision with board
                if (board[newY] && board[newY][newX] !== 0) {
                    return false; // Collision with another piece
                }
            }
        }
    }
    return true;
}


// 1. Piece Rotation
function rotatePiece() {
    if (!activePiece.shape) return;

    // O piece does not rotate
    if (activePiece.color === TETROMINOES['O'].color) { // A bit of a hack to identify 'O'
        return;
    }

    // Create a new matrix for the rotated shape
    const shape = activePiece.shape;
    const N = shape.length; // Assuming square matrices for simplicity, which is true for current tetrominoes
    let newShape = [];
    for (let i = 0; i < N; i++) {
        newShape[i] = [];
        for (let j = 0; j < N; j++) {
            newShape[i][j] = 0;
        }
    }

    // Transpose + Reverse rows for clockwise rotation
    for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) {
            if (shape[y][x]) {
                newShape[x][N - 1 - y] = shape[y][x];
            }
        }
    }

    // Trim empty rows/cols from the newShape if necessary (especially for 'I' piece)
    // For simplicity, current tetromino definitions are padded to be square or fit their largest dimension.
    // A more robust solution would trim and adjust piece.x, piece.y.
    // For now, we assume the rotation happens within the existing bounding box.

    if (isValidMove(activePiece.x, activePiece.y, newShape)) {
        activePiece.shape = newShape;
    } else {
        // Basic wall kick: try moving 1 unit left or right
        if (isValidMove(activePiece.x + 1, activePiece.y, newShape)) {
            activePiece.x++;
            activePiece.shape = newShape;
        } else if (isValidMove(activePiece.x - 1, activePiece.y, newShape)) {
            activePiece.x--;
            activePiece.shape = newShape;
        }
        // Could also try moving up once if needed, but that's less standard for Tetris.
    }
}

// 5. Drawing Functions
function drawBlock(x, y, color) {
    context.fillStyle = color;
    context.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    context.strokeStyle = '#333'; // Block border
    context.strokeRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
}

function drawPiece() {
    const piece = activePiece;
    if (!piece.shape) return;
    piece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value > 0) {
                drawBlock(piece.x + x, piece.y + y, piece.color);
            }
        });
    });
}

function drawBoard() {
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (board[r][c]) {
                drawBlock(c, r, board[r][c]); // board stores color of landed blocks
            }
        }
    }
}

// 6. Piece Movement (using isValidMove)
function moveDown() {
    if (isValidMove(activePiece.x, activePiece.y + 1, activePiece.shape)) {
        activePiece.y++;
    } else {
        landPiece();
        // newPiece(); // newPiece is now called after line clearing in landPiece
    }
}

function moveLeft() {
    if (isValidMove(activePiece.x - 1, activePiece.y, activePiece.shape)) {
        activePiece.x--;
    }
}

function moveRight() {
    if (isValidMove(activePiece.x + 1, activePiece.y, activePiece.shape)) {
        activePiece.x++;
    }
}

// The old collision() function is no longer needed as isValidMove covers its functionality.

// 3. Line Clearing
function clearLines() {
    let linesCleared = 0;
    for (let r = ROWS - 1; r >= 0; r--) {
        let isRowFull = true;
        for (let c = 0; c < COLS; c++) {
            if (board[r][c] === 0) {
                isRowFull = false;
                break;
            }
        }

        if (isRowFull) {
            linesCleared++;
            // Remove the row and add a new empty row at the top
            board.splice(r, 1);
            board.unshift(Array(COLS).fill(0));
            r++; // Re-check the current row index as rows shifted down
        }
    }
    return linesCleared;
}

// 4. Score Management
let score = 0;
const scoreElement = document.getElementById('score');

function updateScore(linesCleared) {
    if (linesCleared > 0) {
        let lineScore = 100 * linesCleared; // Base score
        if (linesCleared === 4) { // Tetris bonus
            lineScore *= 2;
        } else if (linesCleared > 1) {
            lineScore *= 1.5; // Bonus for multiple lines
        }
        score += lineScore;
    }
    scoreElement.textContent = score;
}
function resetScore() {
    score = 0;
    scoreElement.textContent = score;
}


function landPiece() {
    const piece = activePiece;
    if (!piece.shape) return;
    piece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value > 0) {
                if ((piece.y + y >= 0) && (piece.y + y < ROWS) && (piece.x + x >=0) && (piece.x + x < COLS) ) {
                     board[piece.y + y][piece.x + x] = piece.color;
                }
            }
        });
    });

    const linesCleared = clearLines();
    updateScore(linesCleared);

    newPiece(); // Spawn next piece
    // Game over check is now primarily in newPiece
}


// 7. Game Loop
let gameInterval = null;
let isPaused = false;
const GAME_SPEED = 500; // Milliseconds

function gameLoop() {
    if (isPaused) return;

    // The moveDown() call is the primary action in the game loop that can lead to landing.
    // We need to draw *before* moveDown to show the piece in its current position,
    // and then *after* moveDown (or after landing and new piece) to show the updated state.

    context.clearRect(0, 0, canvas.width, canvas.height);
    drawBoard();
    drawPiece(); // Draw current piece before it moves

    moveDown(); // This will handle landing, line clearing, and new piece spawning internally

    // No need to call drawBoard/drawPiece again here as moveDown and subsequent calls handle it
    // or the next gameLoop iteration will.
}

// 5. Game Over Condition
function handleGameOver() {
    clearInterval(gameInterval);
    gameInterval = null;
    isPaused = true; // Stop any further game actions
    context.fillStyle = 'rgba(0,0,0,0.75)';
    context.fillRect(0, canvas.height / 2 - 30, canvas.width, 60);
    context.font = '24px Arial';
    context.fillStyle = 'white';
    context.textAlign = 'center';
    context.fillText('Game Over!', canvas.width / 2, canvas.height / 2);
    console.log("Game Over. Final Score:", score);
    startButton.disabled = false; // Allow restart
    startButton.textContent = 'Restart';
    pauseButton.disabled = true;
}


// Refined newPiece to include game over check
function newPiece() {
    const randomPieceType = PIECES[Math.floor(Math.random() * PIECES.length)];
    const pieceDetails = TETROMINOES[randomPieceType];
    activePiece.shape = pieceDetails.shape;
    activePiece.color = pieceDetails.color;
    // Start piece slightly off-center for some shapes, then adjust
    activePiece.x = Math.floor(COLS / 2) - Math.ceil(activePiece.shape[0].length / 2);
    activePiece.y = 0; // Start at the very top

    if (!isValidMove(activePiece.x, activePiece.y, activePiece.shape)) {
        // If the new piece immediately collides, it's game over
        handleGameOver();
        return; // Stop further execution for this piece
    }
}


// 8. Initialization
function init() {
    initBoard();
    resetScore();
    newPiece(); // Spawns the first piece and checks for immediate game over

    if (gameInterval) { // Clear any existing interval
        clearInterval(gameInterval);
    }

    if (!isValidMove(activePiece.x, activePiece.y, activePiece.shape)) {
        // This case should ideally be caught by newPiece itself, but as a safeguard:
        handleGameOver();
        return;
    }

    isPaused = false;
    gameInterval = setInterval(gameLoop, GAME_SPEED);
    startButton.disabled = true;
    startButton.textContent = 'Start'; // Reset button text
    pauseButton.disabled = false;
    pauseButton.textContent = 'Pause';
}

// Event Listeners for buttons
const startButton = document.getElementById('start');
const pauseButton = document.getElementById('pause');

startButton.addEventListener('click', () => {
    init(); // init now handles reset and start
});

pauseButton.addEventListener('click', () => {
    if (isPaused) {
        isPaused = false;
        gameInterval = setInterval(gameLoop, GAME_SPEED); // Resume game
        pauseButton.textContent = 'Pause';
    } else {
        if(gameInterval){ // Only pause if game is actually running
            isPaused = true;
            clearInterval(gameInterval);
            gameInterval = null; // Important to nullify to distinguish from not started
            pauseButton.textContent = 'Resume';
        }
    }
});


// Initial setup - game does not start automatically
initBoard();
drawBoard(); // Draw empty board initially
// newPiece(); // Don't spawn piece until start is pressed
// drawPiece();
pauseButton.disabled = true;
startButton.disabled = false; // Start button should be enabled


// Keyboard controls
document.addEventListener('keydown', (event) => {
    if (isPaused && event.key !== 'Escape') return; // Allow escape to potentially unpause or for other menus later
    if (!gameInterval && isPaused) { // Game is paused (not just before start)
         if (event.key === 'p' || event.key === 'P' || event.key === 'Escape') { // Common pause keys
            pauseButton.click(); // Simulate click to resume
        }
        return;
    }
    if (!gameInterval && !isPaused) return; // Game hasn't started and isn't paused (i.e. initial state)


    let needsRedraw = false;
    switch (event.key) {
        case 'ArrowLeft':
            moveLeft();
            needsRedraw = true;
            break;
        case 'ArrowRight':
            moveRight();
            needsRedraw = true;
            break;
        case 'ArrowDown':
            moveDown();
            needsRedraw = true; // moveDown itself will cause redraw via gameLoop or landing
            break;
        case 'ArrowUp':
            rotatePiece();
            needsRedraw = true;
            break;
        case ' ': // Spacebar for hard drop (optional future feature)
            // while (isValidMove(activePiece.x, activePiece.y + 1, activePiece.shape)) {
            //     activePiece.y++;
            // }
            // landPiece();
            // needsRedraw = true;
            break;
    }

    if (needsRedraw && !isPaused && gameInterval) {
        // Redraw immediately after key press for responsiveness,
        // but only if the game is running and not paused.
        context.clearRect(0, 0, canvas.width, canvas.height);
        drawBoard();
        drawPiece();
    }
});

console.log("Tetris game script loaded and enhanced.");
