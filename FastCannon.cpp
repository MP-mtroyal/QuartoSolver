#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <math.h>
#include <stdio.h>

namespace py = pybind11;

// ----------- Fast Cannonization Functions ----------
void boxRotate4x4(short* board);
void innerRotate4x4(short* board);
void rotate(short* board);
void verticalAxisFlip(short* board);
void horizontalAxisFlip(short* board);
void tranpose4x4(short* board);
void copyBoard(short* src, short* dst, int size);
int getCandidateType(short* board);
int getXOR(short* board);
void boardXOR(short* board, int xorPiece, int boardSize);
int64_t evaluateBoard(short* board, int boardSize);

//--------------- Fast Board Functions ------------
bool checkFeatList(int* pieces, int numPieces);
bool PlacePiece(py::array_t<short> board, int x, int y, int piece);
int cannonizeBoardTransforms(short* brdPtr, int boardSize);

/*
Indices for contigious array
0, 4, 8, 12
1, 5, 9, 13
2, 6, 10, 14
3, 7, 11, 15
*/


void transformBoard(short* board, int transformIndex){
    int baseStructIndex = transformIndex & 3;
    int d4index = transformIndex >> 2;
    //====== Base Struct Transformations ============
    switch (baseStructIndex) {
    case 0: //identity
        break;
    case 1: boxRotate4x4(board); break;
    case 2: innerRotate4x4(board); break;
    case 3:
        boxRotate4x4(board);
        innerRotate4x4(board);
        break;
    }
    //======= Dihedral 4 Transformations =========
    switch (d4index)
    {
    case 0: //Identity
        break;
    case 1:
        rotate(board);
        rotate(board);
        rotate(board);
        break;
    case 2:
        rotate(board);
        rotate(board);
        break;
    case 3:
        rotate(board);
        break;
    case 4:
        verticalAxisFlip(board);
        break;
    case 5:
        horizontalAxisFlip(board);
        break;
    case 6:
        tranpose4x4(board);
        break;
    case 7:
        tranpose4x4(board);
        horizontalAxisFlip(board);
        verticalAxisFlip(board);
        break;
    }
}

void boxRotate4x4(short* board){
    int temp;
    int swaps1[] = {0, 1, 2, 3, 8, 9, 10, 11};
    int swaps2[] = {5, 4, 7, 6, 13, 12, 15, 14};
    for (int i=0; i<8; i++){
        temp = board[swaps1[i]];
        board[swaps1[i]] = board[swaps2[i]];
        board[swaps2[i]] = temp;
    }
}

void innerRotate4x4(short* board){
    int temp;
    int swaps1[] = {1, 4, 7, 13, 5, 9};
    int swaps2[] = {2, 8, 11, 14, 10, 6};
    for (int i=0; i<6; i++){
        temp = board[swaps1[i]];
        board[swaps1[i]] = board[swaps2[i]];
        board[swaps2[i]] = temp;
    }
}

//CCW rotation by 90 degrees
void rotate(short* board){
    int temp;
    int chainLength = 4;
    int chainCount  = 4;
    int chain[4][4] = {
        {0, 12, 15, 3},
        {4, 13, 11, 2},
        {8, 14, 7, 1},
        {5, 9, 10, 6}
    };

    for (int n=0; n<chainCount; n++){
        temp = board[chain[n][0]];
        for (int i=0; i<chainLength-1; i++){
            board[chain[n][i]] = board[chain[n][i+1]];
        }
        board[chain[n][chainLength-1]] = temp;
    }
}

void verticalAxisFlip(short* board){
    int temp;
    int swaps1[] = {0, 1, 2, 3, 4, 5, 6, 7};
    int swaps2[] = {12, 13, 14, 15, 8, 9, 10, 11};
    for (int i=0; i<8; i++){
        temp = board[swaps1[i]];
        board[swaps1[i]] = board[swaps2[i]];
        board[swaps2[i]] = temp;
    }
}

void horizontalAxisFlip(short* board){
    int temp;
    int swaps1[] = {0, 1, 4, 5, 8, 9, 12, 13};
    int swaps2[] = {3, 2, 7, 6, 11, 10, 15, 14};
    for (int i=0; i<8; i++){
        temp = board[swaps1[i]];
        board[swaps1[i]] = board[swaps2[i]];
        board[swaps2[i]] = temp;
    }
}

void tranpose4x4(short* board){
    int temp;
    int swaps1[] = {1, 2, 3, 6, 7, 11};
    int swaps2[] = {4, 8, 12, 9, 13, 14};
    for (int i=0; i<6; i++){
        temp = board[swaps1[i]];
        board[swaps1[i]] = board[swaps2[i]];
        board[swaps2[i]] = temp;
    }
}

void copyBoard(short* src, short* dst, int size){
    for (int i=0; i<size; i++){
        dst[i] = src[i];
    }
}

int getCandidateType(short* board){
    if (board[0] >= 0) {return 1;}
    if (board[1] >= 0) {return 2;}
    return -1;
}

int getXOR(short* board){
    if (board[0] >= 0) {return board[0];}
    if (board[1] >= 0) {return board[1];}
    return -1;
}

void boardXOR(short* board, int xorPiece, int boardSize){
    for (int i=0; i<boardSize; i++){
        if (board[i] >= 0){
            board[i] = board[i] ^ xorPiece;
        }
    }
}

int64_t evaluateBoard(short* board, int boardSize){
    int64_t boardHash = 0;
    for(int i=1; i<boardSize; i++){
        if (board[i] >= 0){
            boardHash += board[i] << (4 * (i-1));
        }
    }
    return boardHash;
}

void printBoard(short *brdPtr, int boardSize){
    char outStr[2] = {'A', '\0'};
    for (int i=0; i<boardSize; i++){
        if (brdPtr[i] >= 0){
            outStr[0] = brdPtr[i] + '0';
            printf(outStr);
            printf(", ");
        }
    }
    printf("\n");
}

int cannonizeBoardTransforms(short *brdPtr, int boardSize){
    short* bestBoard = (short*)malloc(boardSize * sizeof(short));
    short* buffBoard = (short*)malloc(boardSize * sizeof(short));
    
    int64_t bestHash = 0;
    int64_t currHash = 0;
    int bestXor = -1;
    int currXor = -1;
    int bestBoardIndex = -1;
    int bestCandidateType = -1;
    int currCandidateType = -1;

    for (int i=0; i<32; i++){
        // Copy base board into board buffer
        copyBoard(brdPtr, buffBoard, boardSize);
        // Apply Unique transform
        transformBoard(buffBoard, i);
        currXor = getXOR(buffBoard);
        // Don't consider the board if no valid XOR piece exists
        if(currXor < 0){continue;}

        currCandidateType = getCandidateType(buffBoard);
        // Candidate type not yet selected
        if (bestCandidateType < 0){ bestCandidateType = currCandidateType;} 
        else if (bestCandidateType == 2 && currCandidateType == 1){
            bestCandidateType = currCandidateType;
            bestBoardIndex = -1;
        }
        // Board is wrong candidateType
        else if(currCandidateType != bestCandidateType) {continue;} 

        boardXOR(buffBoard, currXor, boardSize);

        currHash = evaluateBoard(buffBoard, boardSize);

        // Copy into best board if new best is found
        if (bestBoardIndex < 0 || currHash < bestHash){
            bestBoardIndex = i;
            bestHash = currHash;
            bestXor = currXor;
            copyBoard(buffBoard, bestBoard, boardSize);
        }
    }

    // Do not copy if no candidate boards exist
    if (bestBoardIndex >= 0){
        //Copy over best board
        copyBoard(bestBoard, brdPtr, boardSize);
    }

    free(bestBoard);
    free(buffBoard);

    return bestXor;
}

int numOnesInBinStr(int binStr) {
    int count = 0;
    if (binStr < 0) { return count; }
    while (binStr > 0) {
        if (binStr % 2 == 1) {
            count++;
        }
        binStr = binStr >> 1;
    }
    return count;
}

bool featureBitSwap(
    short* brdPtr, 
    int boardSize, 
    uint8_t* remPtr,
    int remSize,
    int* selectPtr,
    int selectSize,
    int bitPos, 
    int thresh
){
    int posMask = 15 - ((1 << bitPos) - 1);
    int swapMask = -1;
    int maskedVal, shiftCount, currPiece;
    uint8_t remDummyArr[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

    for (int i = 0; i < boardSize; i++) {
        if (brdPtr[i] > 0) {
            maskedVal = brdPtr[i] & posMask;
            if (maskedVal > 0 && numOnesInBinStr(maskedVal) == thresh) {
                shiftCount = 0;
                while (maskedVal % 2 == 0) {
                    maskedVal = maskedVal >> 1;
                    shiftCount++;
                }
                if (shiftCount == bitPos) {
                    return true;
                }
                else {
                    swapMask = (1 << shiftCount) + (1 << bitPos);
                }
                break;
            }
        }
    }

    if (swapMask < 0)
        return false;

    // Swap board piece features
    for (int i = 0; i < boardSize; i++) {
        currPiece = brdPtr[i];
        if ((currPiece > 0) && 
            ((currPiece & swapMask) != swapMask) && 
            ((currPiece & swapMask) != 0)) 
        {
            brdPtr[i] = currPiece ^ swapMask;
        }
    }

    // Swap selected piece features
    for (int i=0; i<selectSize; i++){
        currPiece = selectPtr[i];
        if ((currPiece > 0) && 
            ((currPiece & swapMask) != swapMask) && 
            ((currPiece & swapMask) != 0)) 
        {
            selectPtr[i] = currPiece ^ swapMask;
        }
    }

    // Swap Remaining piece features
    for (int i=0; i<remSize; i++){
        if (remPtr[i] == 1){
            if (((i & swapMask) != swapMask) && ((i & swapMask) != 0)) {
                remDummyArr[i ^ swapMask] = 1;
            } else {
                remDummyArr[i] = 1;
            }
        } 
    }
    for (int i=0; i<remSize; i++){
        remPtr[i] = remDummyArr[i];
    }

    return true;
}

void ApplyFeatureSwaps(py::array_t<short> board, py::array_t<uint8_t> remPieces, py::array_t<int> selPieces){
    // Get buffer info (allows access to raw data)
    py::buffer_info buf = board.request();
    // Ensure it's mutable
    if (buf.readonly) {
        throw std::runtime_error("Input array is not writable!");
    }
    short* brdPtr = static_cast<short*>(buf.ptr);
    int boardSize = static_cast<int>(buf.size);
    
    // Get rem pieces buffer
    py::buffer_info remBuf = board.request();
    // Ensure it's mutable
    if (remBuf.readonly) {
        throw std::runtime_error("Input array is not writable!");
    }
    uint8_t* remPtr = static_cast<uint8_t*>(remBuf.ptr);
    int remPiecesCount = static_cast<int>(remBuf.size);

    // Get rem pieces buffer
    py::buffer_info selectBuf = board.request();
    // Ensure it's mutable
    if (selectBuf.readonly) {
        throw std::runtime_error("Input array is not writable!");
    }
    int* selectPtr = static_cast<int*>(selectBuf.ptr);
    int selectPiecesCount = static_cast<int>(selectBuf.size);


    bool success = featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 0, 1);
    if (success) {
        bool success = featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 1, 1);
        if (success) {
            featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 2, 1);
        }
        else {
            bool success = featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 1, 2);
            if (success) {
                featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 2, 3);
            }
        }
    }
    else {
        bool success = featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 0, 2);
        if (success) {
            featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 1, 2);
            featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 2, 1);
        }
        else {
            bool success = featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 0, 3);
            if (success) {
                featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 1, 2);
                featureBitSwap(brdPtr, boardSize, remPtr, remPiecesCount, selectPtr, selectPiecesCount, 2, 1);
            }
        }
    }
}

void xorPieces(int* selectPtr, int selectSize, uint8_t* remPtr, int remSize, int xorPiece){
    if (xorPiece < 0 || xorPiece > remSize){
        return;
    }
    for(int i=0; i<selectSize; i++){
        selectPtr[i] = selectPtr[i] ^ xorPiece;
    }

    uint8_t remDummyArr[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    // Swap Remaining piece features
    for (int i=0; i<remSize; i++){
        if (((i & xorPiece) != xorPiece) && ((i & xorPiece) != 0)) {
            remDummyArr[i ^ xorPiece] = 1;
        }
    }
    for (int i=0; i<remSize; i++){
        remPtr[i] = remDummyArr[i];
    }
}

int cannonize(py::array_t<short> board) {
    // Get buffer info (allows access to raw data)
    py::buffer_info buf = board.request();
    // Ensure it's mutable
    if (buf.readonly) {
        throw std::runtime_error("Input array is not writable!");
    }
    short* brdPtr = static_cast<short*>(buf.ptr);
    int boardSize = static_cast<int>(buf.size);

    int boardXOR = cannonizeBoardTransforms(brdPtr, boardSize);

    return boardXOR;
}

bool checkFeatList(int* pieces, int numPieces){
    int andCmp = 15;
    int orCmp = 0;
    for (int i=0; i<numPieces; i++){
        if (pieces[i] < 0){return false;}
        andCmp = andCmp & pieces[i];
        orCmp  = orCmp | pieces[i];
    }
    return andCmp != 0 || 15 - orCmp != 0;
}

bool PlacePiece(py::array_t<short> board, int x, int y, int piece){
    int featList[4] = {0,0,0,0};
    py::buffer_info buf = board.request();
    short* ptr = static_cast<short*>(buf.ptr);

    ptr[x*4 + y] = piece;

    for(int i=0; i<4; i++){featList[i] = ptr[x*4 + i];}
    if (checkFeatList(featList, 4)){return true;}
    for(int i=0; i<4; i++){featList[i] = ptr[y + i];}
    if (checkFeatList(featList, 4)){return true;}
    if(x % 4 == y){ //diagonal 1
        for(int i=0; i<4; i++){featList[i] = ptr[i*4 + i];}
        if (checkFeatList(featList, 4)){return true;}
    }
    if (x % 4 + y == 3){
        for(int i=0; i<4; i++){featList[i] = ptr[(3-i)*4 + i];}
        if (checkFeatList(featList, 4)){return true;}
    } 
    return false;
}


PYBIND11_MODULE(FastCannon, m) {
    m.def("cannonize", &cannonize, "Fast Quarto Cannonization");
    m.def("placePiece", &PlacePiece, "Place Piece Quickly");
}


