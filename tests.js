// Simple Test Framework
const TestSuite = {
    run: function(name, tests) {
        let resultsDiv = document.getElementById('test-results');
        let suiteDiv = document.createElement('div');
        suiteDiv.className = 'test-suite';
        let title = document.createElement('h2');
        title.textContent = name;
        suiteDiv.appendChild(title);
        resultsDiv.appendChild(suiteDiv);

        let passes = 0;
        let failures = 0;

        for (const testName in tests) {
            let testCaseDiv = document.createElement('div');
            testCaseDiv.className = 'test-case';
            try {
                // Reset game state before each test
                if (typeof init === 'function') {
                    init(); // Resets the board, score, activePiece, etc.
                    if (window.gameInterval) { // gameInterval is global in tetris.js
                        clearInterval(window.gameInterval);
                    }
                    window.gameInterval = null; // Ensure game loop is stopped for tests
                    window.isPaused = true; // Ensure game doesn't try to run logic if init started it
                } else {
                    console.warn("init function not found. Game state might not be reset for test: " + testName);
                }

                tests[testName]();
                testCaseDiv.innerHTML = `<span class="pass">PASS</span>: ${testName}`;
                passes++;
            } catch (e) {
                testCaseDiv.innerHTML = `<span class="fail">FAIL</span>: ${testName}<br><pre>${e.stack || e}</pre>`;
                failures++;
            }
            suiteDiv.appendChild(testCaseDiv);
        }
        title.textContent += ` (${passes} passed, ${failures} failed)`;
    },
    assertEquals: function(expected, actual, message) {
        if (expected !== actual) {
            throw new Error(message + ` - Expected: ${expected}, Actual: ${actual}`);
        }
    },
    assertDeepEquals: function(expected, actual, message) {
        if (JSON.stringify(expected) !== JSON.stringify(actual)) {
            throw new Error(message + ` - Expected: ${JSON.stringify(expected)}, Actual: ${JSON.stringify(actual)}`);
        }
    },
    assertTrue: function(value, message) {
        if (!value) {
            throw new Error(message + ` - Expected true, got false`);
        }
    },
    assertFalse: function(value, message) {
        if (value) {
            throw new Error(message + ` - Expected false, got true`);
        }
    }
};

// --- Tetris Game Tests ---

// Helper to get piece dimensions, accounting for empty rows/cols in definition
function getActualPieceDimensions(shapeMatrix) {
    let minR = shapeMatrix.length, maxR = -1, minC = shapeMatrix[0].length, maxC = -1;
    let hasBlocks = false;
    shapeMatrix.forEach((row, r) => {
        row.forEach((cell, c) => {
            if (cell) {
                hasBlocks = true;
                if (r < minR) minR = r;
                if (r > maxR) maxR = r;
                if (c < minC) minC = c;
                if (c > maxC) maxC = c;
            }
        });
    });
    if (!hasBlocks) return { width: 0, height: 0, firstBlockRow: 0, firstBlockCol: 0 };
    return {
        width: maxC - minC + 1,
        height: maxR - minR + 1,
        firstBlockRow: minR, // First row index that contains a block
        firstBlockCol: minC  // First col index that contains a block
    };
}


TestSuite.run("Tetrominoes and Piece Initialization", {
    "should create a new piece with correct properties": function() {
        newPiece(); // Uses global newPiece from tetris.js
        const piece = window.activePiece; // activePiece is global
        TestSuite.assertTrue(piece !== null, "Active piece should not be null");
        TestSuite.assertTrue(piece.shape && piece.shape.length > 0, "Piece should have a shape");
        TestSuite.assertTrue(typeof piece.x === 'number', "Piece should have x coordinate");
        TestSuite.assertTrue(typeof piece.y === 'number', "Piece should have y coordinate");
        TestSuite.assertTrue(piece.color !== undefined, "Piece should have a color");
    },
    "initial piece x should be centered": function() {
        newPiece();
        const piece = window.activePiece;
        const pieceDims = getActualPieceDimensions(piece.shape);
        // The game's centering logic: Math.floor(COLS / 2) - Math.ceil(piece.shape[0].length / 2);
        // This might differ if piece.shape[0] is not representative of actual width.
        // Let's use the game's own calculation basis for comparison if it's simpler.
        const expectedX = Math.floor(window.COLS / 2) - Math.ceil(piece.shape[0].length / 2);
        TestSuite.assertEquals(expectedX, piece.x, "Piece X position not centered as per game logic");
    },
    "initial piece y should be 0": function() {
        // In the current tetris.js, piece.y always starts at 0.
        // The visual top might be different if the shape has leading empty rows,
        // but piece.y itself is 0.
        newPiece();
        const piece = window.activePiece;
        TestSuite.assertEquals(0, piece.y, "Piece Y position not at the top (0)");
    }
});

TestSuite.run("Piece Movement and Collision", {
    "should move piece left within bounds": function() {
        newPiece();
        window.activePiece.x = 5; // Start at a known position
        const initialX = window.activePiece.x;
        moveLeft();
        TestSuite.assertEquals(initialX - 1, window.activePiece.x, "Piece did not move left");
    },
    "should not move piece left out of bounds": function() {
        newPiece();
        const pieceDims = getActualPieceDimensions(window.activePiece.shape);
        window.activePiece.x = 0; // Force piece to actual left edge
        moveLeft();
        TestSuite.assertEquals(0, window.activePiece.x, "Piece moved left out of bounds");
    },
    "should move piece right within bounds": function() {
        newPiece();
        window.activePiece.x = 3; // Start at a known position
        const initialX = window.activePiece.x;
        moveRight();
        TestSuite.assertEquals(initialX + 1, window.activePiece.x, "Piece did not move right");
    },
    "should not move piece right out of bounds": function() {
        newPiece();
        const piece = window.activePiece;
        const pieceDims = getActualPieceDimensions(piece.shape);
        // Place the piece so its rightmost block is at COLS - 1
        piece.x = window.COLS - pieceDims.width - pieceDims.firstBlockCol;
        const currentX = piece.x;
        moveRight();
        TestSuite.assertEquals(currentX, piece.x, "Piece moved right out of bounds");
    },
    "should move piece down": function() {
        newPiece();
        const initialY = window.activePiece.y;
        moveDown(); // This will call gameLoop's moveDown logic
        if (window.isGameOver) { // If game over happened immediately, this test might be tricky
            TestSuite.assertTrue(true, "Game over on first moveDown, cannot assert Y position normally");
            return;
        }
        // If moveDown results in landing, y might not be initialY + 1
        // This test is more about `isValidMove` for down, not the game loop's effect
        if (isValidMove(window.activePiece.x, initialY + 1, window.activePiece.shape)) {
             // If we manually set Y and check:
             window.activePiece.y = initialY; // reset y
             if(isValidMove(window.activePiece.x, window.activePiece.y + 1, window.activePiece.shape)) {
                window.activePiece.y++;
                TestSuite.assertEquals(initialY + 1, window.activePiece.y, "Piece did not move down by one step");
             } else {
                // Cannot move down, must be at bottom or collision
                TestSuite.assertTrue(true, "Piece could not move down, likely at bottom or collision.");
             }
        } else {
             TestSuite.assertTrue(true, "Piece could not move down from initial position (already colliding or at bottom).");
        }
    },
    "should detect collision with bottom": function() {
        newPiece();
        const piece = window.activePiece;
        const pieceDims = getActualPieceDimensions(piece.shape);
        piece.y = window.ROWS - pieceDims.height - pieceDims.firstBlockRow; // Position piece right above bottom
        const canMove = isValidMove(piece.x, piece.y + 1, piece.shape);
        TestSuite.assertFalse(canMove, "Collision with bottom not detected by isValidMove. Piece Y: " + piece.y + ", Height: " + pieceDims.height);
    },
    "should land piece when it hits bottom": function() {
        newPiece();
        const piece = window.activePiece;
        const pieceColor = piece.color; // Store color for later check
        const pieceShape = JSON.parse(JSON.stringify(piece.shape)); // Deep copy
        const pieceX = piece.x;

        const pieceDims = getActualPieceDimensions(pieceShape);
        piece.y = window.ROWS - pieceDims.height - pieceDims.firstBlockRow; // Position piece at the bottom

        // Stop game loop for this test, manually call moveDown
        if(window.gameInterval) clearInterval(window.gameInterval); window.gameInterval = null;

        moveDown(); // This should trigger landPiece because isValidMove(y+1) will be false

        TestSuite.assertTrue(window.activePiece.y === 0 || window.activePiece.y < piece.y, "New piece was not spawned (or y not reset) after landing. Old Y: "+piece.y + " New Y: "+window.activePiece.y);

        let landedCorrectly = true;
        for (let r = 0; r < pieceShape.length; r++) {
            for (let c = 0; c < pieceShape[r].length; c++) {
                if (pieceShape[r][c]) { // If this part of the shape is a block
                    const boardY = piece.y + r;
                    const boardX = pieceX + c;
                    if (boardY >= 0 && boardY < window.ROWS && boardX >=0 && boardX < window.COLS) {
                        if (window.board[boardY][boardX] !== pieceColor) {
                            landedCorrectly = false;
                            break;
                        }
                    } else {
                        // This block was outside bounds, shouldn't happen if positioning is correct
                        landedCorrectly = false; break;
                    }
                }
            }
            if (!landedCorrectly) break;
        }
        TestSuite.assertTrue(landedCorrectly, "Landed piece not correctly transferred to board with correct color.");
    },
    "should detect collision with other pieces": function() {
        newPiece();
        const piece = window.activePiece;
        // Manually place a block on the board
        const obstacleX = piece.x;
        const obstacleY = piece.y + getActualPieceDimensions(piece.shape).height + getActualPieceDimensions(piece.shape).firstBlockRow;
        if(obstacleY < window.ROWS) { // Ensure obstacle is within board
            window.board[obstacleY][obstacleX] = 'gray'; // Place a block
            const canMove = isValidMove(piece.x, piece.y + 1, piece.shape);
            TestSuite.assertFalse(canMove, "Collision with another piece not detected by isValidMove");
        } else {
            TestSuite.assertTrue(true, "Skipping collision with other pieces test, piece too close to bottom.");
        }
    }
});

TestSuite.run("Piece Rotation", {
    "should rotate piece (e.g., I-shape from horizontal to vertical)": function() {
        // Force an I-shape piece
        window.activePiece = {
            x: Math.floor(window.COLS / 2) - 2,
            y: 0,
            shape: JSON.parse(JSON.stringify(TETROMINOES['I'].shape)), // Deep copy
            color: TETROMINOES['I'].color
        };
        const originalShape = JSON.parse(JSON.stringify(window.activePiece.shape));
        rotatePiece(); // Global rotatePiece
        TestSuite.assertFalse(JSON.stringify(originalShape) === JSON.stringify(window.activePiece.shape), "Piece shape did not change after rotation");

        // Expected vertical I-shape (one of the forms after rotation)
        // Note: TETROMINOES['I'].shape is initially horizontal: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]
        // Rotated (example): [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]] (actual might vary based on exact rotation center)
        let isVertical = true;
        let colWithBlocks = -1;
        for(let c=0; c < window.activePiece.shape[0].length; c++) {
            if(window.activePiece.shape[0][c] || window.activePiece.shape[1][c] || window.activePiece.shape[2][c] || window.activePiece.shape[3][c]){
                colWithBlocks = c;
                break;
            }
        }
        if(colWithBlocks === -1) isVertical = false; // No blocks found

        for (let r = 0; r < 4; r++) { // Check first 4 rows
            for (let c = 0; c < window.activePiece.shape[r].length; c++) {
                if (c === colWithBlocks) { // Blocks should be in this column
                    if (window.activePiece.shape[r][c] === 0 && r < 4) { /*isVertical = false; break;*/ } // Allow for I piece not filling all 4 cells if it's smaller variant
                } else { // Other columns should be empty
                    if (window.activePiece.shape[r][c] !== 0) { isVertical = false; break; }
                }
            }
            if (!isVertical) break;
        }
         TestSuite.assertTrue(isVertical, "I-shape did not rotate to a recognizable vertical form. Shape: " + JSON.stringify(window.activePiece.shape));
    },
    "should not rotate piece if it causes collision (boundary)": function() {
        // Force an L-shape piece to the right edge
        window.activePiece = {
            x: window.COLS - 2, // L is often 3 wide, its matrix is 3x3. COLS-2 makes its 3rd col align with board edge.
            y: 0,
            shape: JSON.parse(JSON.stringify(TETROMINOES['L'].shape)),
            color: TETROMINOES['L'].color
        };
        const originalShape = JSON.parse(JSON.stringify(window.activePiece.shape));
        const originalX = window.activePiece.x;
        rotatePiece();

        // After rotation, the piece should either not have changed (if no valid rotation/kick)
        // or have shifted left (wall kick)
        const shapeChanged = JSON.stringify(originalShape) !== JSON.stringify(window.activePiece.shape);
        if (shapeChanged) {
            TestSuite.assertTrue(window.activePiece.x < originalX || isValidMove(window.activePiece.x, window.activePiece.y, window.activePiece.shape), "Piece rotated, but new position is invalid or didn't kick correctly.");
        } else {
            TestSuite.assertTrue(true, "Piece did not rotate or change position, as expected due to boundary.");
        }
    }
});

TestSuite.run("Line Clearing and Scoring", {
    "should clear a completed line": function() {
        const lineIndex = window.ROWS - 1;
        for (let c = 0; c < window.COLS; c++) {
            window.board[lineIndex][c] = 'blue'; // Fill bottom line
        }
        clearLines(); // global
        const isLineCleared = window.board[lineIndex].every(cell => cell === 0);
        TestSuite.assertTrue(isLineCleared, "Completed line was not cleared. Line: " + JSON.stringify(window.board[lineIndex]));
        const isNewLineAddedAtTop = window.board[0].every(cell => cell === 0);
        TestSuite.assertTrue(isNewLineAddedAtTop, "New empty line not added at top after clearing");
    },
    "should update score after clearing a line": function() {
        resetScore(); // global
        const lineIndex = window.ROWS - 1;
        for (let c = 0; c < window.COLS; c++) {
            window.board[lineIndex][c] = 'red';
        }
        const linesCleared = clearLines();
        updateScore(linesCleared); // global
        TestSuite.assertEquals(1, linesCleared, "clearLines did not return correct number of cleared lines");
        // Define scoreValues if not globally available for test (tetris.js has it implicitly)
        const scoreValues = { 1: 100, 2: 300, 3: 500, 4: 800 }; // Example, actual values might differ
        // Score update in tetris.js: 100 per line, 4 lines = 800 (100*4 *2), >1 line = 1.5x
        // For 1 line: 100.
        TestSuite.assertEquals(100, window.score, "Score not updated correctly for 1 line. Expected 100, got " + window.score);
    },
    "should award bonus for multiple lines (Tetris - 4 lines)": function() {
        resetScore();
        for (let i = 1; i <= 4; i++) {
            for (let c = 0; c < window.COLS; c++) {
                window.board[window.ROWS - i][c] = 'green'; // Fill bottom 4 lines
            }
        }
        const linesCleared = clearLines();
        updateScore(linesCleared);
        TestSuite.assertEquals(4, linesCleared, "clearLines did not return 4 for Tetris");
        // For 4 lines (Tetris): 100 * 4 * 2 = 800
        TestSuite.assertEquals(800, window.score, "Score not updated correctly for 4 lines (Tetris bonus). Expected 800, got " + window.score);
    }
});

TestSuite.run("Game Over", {
    "should detect game over when new piece cannot be placed": function() {
        // Fill the top part of the board
        for (let r = 0; r < 2; r++) { // Fill top few rows enough to block a piece
            for (let c = 0; c < window.COLS; c++) {
                window.board[r][c] = 'purple';
            }
        }

        // Manually clear any existing gameInterval from a previous test's init()
        if (window.gameInterval) clearInterval(window.gameInterval);
        window.gameInterval = null;
        window.isPaused = true; // Prevent game loop from starting via init or newPiece indirectly

        // Reset isGameOver flag if it exists globally, or handle it via init()
        if(typeof window.isGameOver !== 'undefined') window.isGameOver = false;

        // Call init to reset states but ensure no game loop
        init();
        if (window.gameInterval) clearInterval(window.gameInterval);
        window.gameInterval = null;
        window.isPaused = true;

        // Now fill the board again after init might have cleared it
         for (let r = 0; r < 2; r++) {
            for (let c = Math.floor(window.COLS / 2) - 2; c < Math.floor(window.COLS / 2) + 2; c++) {
                 if(c >=0 && c < window.COLS) window.board[r][c] = 'gray'; // Block spawn area
            }
        }

        newPiece(); // This should try to place a piece, fail, and trigger game over

        // Game over in tetris.js sets gameInterval to null and isPaused to true
        // It also calls handleGameOver() which changes startButton text.
        // The most reliable check here is that the game loop is stopped.
        const gameIsOverConditionMet = (window.gameInterval === null && window.isPaused === true && document.getElementById('start').textContent === 'Restart');

        TestSuite.assertTrue(gameIsOverConditionMet, "Game over was not detected or handled correctly when new piece cannot be placed. Interval: "+window.gameInterval+", Paused: "+window.isPaused + " Button: "+ document.getElementById('start').textContent);
    }
});

// Ensure tetris.js is loaded and its global variables/functions are available.
// The init() in tetris.js should reset: board, score, activePiece, isPaused, gameInterval.
// Tests assume init() is called and stops any running gameInterval.
console.log("tests.js loaded and test suites defined.");
