#include "quartoCuda.cuh"
#include "cudaHelpers.cuh"
#include <stdio.h>

#define GAME_SIZE 10
#define BLOCK_SIZE 4
#define X_DIM_LIMIT 65536

// ======== Structs ================================
struct QuartoCuda {
    int board[16];
    int numSelected;
    char selected[16];
    int numAvaliable;
    char avaliable[16];
    int recCounter;
};

// ============= HELPERS ===========================
__device__ bool checkFeatureListCuda(int* feats, int numFeats);


__device__ void LoadGameCuda(QuartoCuda* game, char* data) {
    int dataPieceIndex = 7;
    int dataPieceMaskShift = 0;

    game->numSelected = 0;
    game->numAvaliable = 0;
    game->recCounter = 0;

    char mask1 = data[8]; // pieces 1-8
    char mask2 = data[9]; // pieces 9-16

    for (int i = 15; i >= 0; i--) {
        // Fill selected and avaliable with default values
        game->selected[i] = -1;
        game->avaliable[i] = -1;
        game->board[i] = -1;

        if (i < 8) {
            if (mask1 & (1 << (7 - i))) {
                int currPiece = (data[dataPieceIndex] & (15 << dataPieceMaskShift)) >> dataPieceMaskShift;
                game->board[i] = currPiece;
                dataPieceMaskShift = (dataPieceMaskShift + 4) % 8;
                if (dataPieceMaskShift == 0) {
                    dataPieceIndex -= 1;
                }
            }
        }
        else {
            if (mask2 & (1 << (15 - i))) {
                int currPiece = (data[dataPieceIndex] & (15 << dataPieceMaskShift)) >> dataPieceMaskShift;
                game->board[i] = currPiece;
                dataPieceMaskShift = (dataPieceMaskShift + 4) % 8;
                if (dataPieceMaskShift == 0) {
                    dataPieceIndex -= 1;
                }
            }
        }
    }

    for (int i = 0; i < 16; i++) {
        bool found = false;
        for (int n = 0; n < 16; n++) {
            if (game->board[n] == i) {
                found = true;
                break;
            }
        }
        if (!found) {
            game->avaliable[game->numAvaliable] = i;
            game->numAvaliable += 1;
        }
    }
}

__device__ bool checkWinCuda(QuartoCuda* game) {
    int featList[4];
    //Horizontal I think
    for (int i = 0; i < 16; i += 4) {
        if (checkFeatureListCuda(game->board + i, 4))
            return true;
    }
    //Vertical I think
    for (int i = 0; i < 4; i++) {
        for (int n = 0; n < 4; n++) {
            featList[n] = game->board[i + (4 * n)];
        }
        if (checkFeatureListCuda(featList, 4))
            return true;
    }
    //Diagonal
    for (int i = 0; i < 4; i++) {
        featList[i] = game->board[i + (i * 4)];
    }
    if (checkFeatureListCuda(featList, 4))
        return true;
    // Anti Diagonal
    for (int i = 0; i < 4; i++) {
        featList[i] = game->board[i + ((3 - i) * 4)];
    }
    if (checkFeatureListCuda(featList, 4))
        return true;
    return false;
}

__device__ bool checkFeatureListCuda(int* feats, int numFeats) {
    char andCmp = 15;
    char orCmp = 0;
    for (int i = 0; i < numFeats; i++) {
        if (feats[i] < 0)
            return false;
        andCmp = andCmp & feats[i];
        orCmp = orCmp | feats[i];
    }
    return andCmp != 0 || 15 - orCmp != 0;
}

__device__ void removeFromArrayCuda(char* arr, char val, int len) {
    bool found = false;
    for (int i = 0; i < len; i++) {
        if (!found) {
            if (arr[i] == val) {
                found = true;
            }
        }
        else {
            arr[i - 1] = arr[i];
        }
    }
    arr[len - 1] = -1;
}

__device__ void selectPieceCuda(QuartoCuda* game, int piece) {
    // Add piece to end of selected array
    game->selected[game->numSelected] = piece;
    game->numSelected++;
    // Remove piece from avaliable array
    removeFromArrayCuda(game->avaliable, piece, 16);
    game->numAvaliable--;
}


__device__ void deselectPieceCuda(QuartoCuda* game, int piece) {
    // Add piece to end of avaliable array
    game->avaliable[game->numAvaliable] = piece;
    game->numAvaliable++;
    // Remove piece from selected array
    removeFromArrayCuda(game->selected, piece, game->numSelected);
    game->numSelected--;
}

__device__ void placePieceCuda(QuartoCuda* game, int piece, int place) {
    if (game->board[place] >= 0) {
        return;
    }
    game->board[place] = piece;

    removeFromArrayCuda(game->selected, piece, game->numSelected);
    game->numSelected--;
}

__device__ void removePieceCuda(QuartoCuda* game, int piece, int place) {
    game->board[place] = -1;

    game->selected[game->numSelected] = piece;
    game->numSelected++;
}

__device__ void copyStrCuda(char* srcStr, char* dstStr) {
    for (int i = 0; i < 1000; i++) { // dummy counter, just to prevent an infinite loop
        dstStr[i] = srcStr[i];
        if (srcStr[i] == '\0')
            return;
    }
}

__device__ void printGameCuda(QuartoCuda* game) {
    for (int i = 0; i < 16; i++) {
        if (game->board[i] < 0) {
            printf("    ");
        }
        else {
            for (int n = 8; n > 0; n /= 2) {
                if (game->board[i] & n)
                    printf("1");
                else
                    printf("0");
            }
        }
        if (i != 15) {
            if (i % 4 == 3)
                printf("\n----|----|----|----\n");
            else
                printf("|");
        }
    }
    printf("\n");
    // print selected
    printf("Selected: ");
    for (int i = 0; i < game->numSelected; i++) {
        for (int n = 3; n >= 0; n--) {
            if (game->selected[i] & (1 << n)) {
                printf("1");
            }
            else {
                printf("0");
            }
        }
        if (i != game->numSelected - 1) {
            printf(", ");
        }
    }
    printf("\n");

    // print Avaliable
    printf("Avaliable: ");
    for (int i = 0; i < game->numAvaliable; i++) {
        for (int n = 3; n >= 0; n--) {
            if (game->avaliable[i] & (1 << n)) {
                printf("1");
            }
            else {
                printf("0");
            }
        }
        if (i != game->numAvaliable - 1) {
            printf(", ");
        }
    }
    printf("\n\n");
}
// =================================================

__device__ int solveGameRec(
    QuartoCuda* game,
    char* sol,
    int solIndex,
    int depth,
    bool turn,
    bool placingPiece
    ) {
    // ====== Check if game is finished
    
    if (game->recCounter >= 500000) { // Only finds shallow depth solutions
        sol[solIndex] = '-';
        sol[solIndex+1] = '\0';
        return -1;
    }
    game->recCounter++;
    bool isFinal = checkWinCuda(game);

    if (isFinal || game->numAvaliable <= 0) {
        //printf("------------ At Bottom ----------------\n");
        int score = 0;
        if (isFinal) {
            if (turn) { score = 1; }
            else { score = -1; }
        }

        sol[solIndex + 1] = '\0'; // Null termination
        sol[solIndex] = (char)(score + 49); //arbitrary ascii offset
        return score;
    }

    int bestScore = -2;
    int score;
    char bestSol[22];

    // Place Piece
    if (placingPiece) {
        int bestSquare;
        int avalSquares[16];
        int numSquares = 0;
        int currPiece = game->selected[0];
        for (int i = 0; i < 16; i++) {
            if (game->board[i] < 0) {
                avalSquares[numSquares] = i;
                numSquares++;
            }
        }
        for (int i = 0; i < numSquares; i++) {
            placePieceCuda(game, currPiece, avalSquares[i]);
            score = solveGameRec(game, sol, solIndex + 1, depth + 1, turn, false);
            removePieceCuda(game, currPiece, avalSquares[i]);

            if (!turn)
                score *= -1;

            if (score > bestScore) {
                bestScore = score;
                bestSquare = avalSquares[i];
                copyStrCuda(sol + solIndex + 1, bestSol);
            }
            if (bestScore > 0) {
                break;
            }
        }
        if (bestScore < -1) { // should only occur in error, but there are error boards
            for (int n = 0; n < 3; n++) {
                sol[solIndex + n] = 'X';
            }
            return -2;
        }
        copyStrCuda(bestSol, sol + solIndex + 1);
        int squareIndex = ((bestSquare % 4) << 2) + (bestSquare / 4);
        sol[solIndex] = (char)(squareIndex + 64);
        return bestScore;

    }

    // Select Piece

    else {
        int piece;
        int bestPiece = -1;
        // Store avaliable pieces in another arrary to avoid reordering on select/deselect
        char currAvaliable[16];
        for (int i = 0; i < game->numAvaliable; i++) {
            currAvaliable[i] = game->avaliable[i];
        }

        for (int i = 0; i < game->numAvaliable; i++) {
            piece = currAvaliable[i];
            selectPieceCuda(game, piece);
            score = solveGameRec(game, sol, solIndex + 1, depth + 1, !turn, true);
            deselectPieceCuda(game, piece);

            if (turn)
                score *= -1;

            if (score > bestScore) {
                bestScore = score;
                bestPiece = piece;
                copyStrCuda(sol + solIndex + 1, bestSol);
            }
            if (bestScore > 0) {
                break;
            }

        }
        if (bestScore < -1) { // should only occur in error, but there are error boards
            for (int n = 0; n < 3; n++) {
                sol[solIndex + n] = 'X';
            }
            return -2;
        }
        copyStrCuda(bestSol, sol + solIndex + 1);
        sol[solIndex] = (char)(bestPiece + 64);
        return bestScore;
    }
}

__global__ void solveGameKernel(
    char* games, 
    char* sols, 
    int numGames, 
    int solSize
)
{
    int xOffset = blockIdx.x * blockDim.x + threadIdx.x;
    int yOffset = blockIdx.y * blockDim.y + threadIdx.y;

    int index = yOffset * X_DIM_LIMIT + xOffset;

    if (index < numGames) {
        //printf("Starting problem: %d\n", index);
        QuartoCuda game;
        LoadGameCuda(&game, games + index * GAME_SIZE);
        solveGameRec(
            &game,
            sols,
            solSize * index,
            0,
            true,
            false
        );
        if (index % 100 == 0) { // Only print 1 in 100 to make it more readable
            //atomicAdd(successCounter, 100);
            printf("Completed Problem: %d\t in %d\t steps\n", index, game.recCounter);
        }
    }
}

void solveGamesCuda(
    char* loadedGames, 
    char* solutions,
    int numGames,
    int solSize
)
{
    char* cudaGames;
    char* cudaSol;
    int* successCounter;
    cudaMalloc(&cudaGames, numGames * GAME_SIZE * sizeof(char));
    cudaMalloc(&cudaSol, numGames * solSize * sizeof(char));
    // Increase stack size to ensure recursion can work
    // I needed 13.5 Gb VRAM to run a stack size of 65536
    // 32768 worked too, just using 2^16 because I have the VRAM
    size_t newStackSize = 32768;
    cudaDeviceSetLimit(cudaLimitStackSize, newStackSize);

    cudaMemcpy(
        cudaGames,
        loadedGames,
        numGames * GAME_SIZE * sizeof(char),
        cudaMemcpyHostToDevice
    );

    dim3 blockDim(BLOCK_SIZE, BLOCK_SIZE);

    dim3 gridDim(
        (X_DIM_LIMIT + BLOCK_SIZE - 1) / BLOCK_SIZE, 
        (numGames + X_DIM_LIMIT * BLOCK_SIZE - 1) / (X_DIM_LIMIT * BLOCK_SIZE)
    );

    solveGameKernel << <gridDim, blockDim >> > (
        cudaGames,
        cudaSol,
        numGames,
        solSize
    );

    cudaDeviceSynchronize();

    printf("Copying Solutions\n");
    cudaMemcpy(
        solutions,
        cudaSol,
        numGames * solSize * sizeof(char),
        cudaMemcpyDeviceToHost
    );
    printf("Finished Copying\n");

    cudaFree(cudaGames);
    cudaFree(cudaSol);
}
