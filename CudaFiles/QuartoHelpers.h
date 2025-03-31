#pragma once

struct Quarto {
	int board[16];
	int numSelected;
	char selected[16];
	int numAvaliable;
	char avaliable[16];
	int numPlaced;
};

void printGame(Quarto* game);
void LoadGame(Quarto* game, char* data);
bool checkWin(Quarto* game);
bool checkFeatureList(int* feats, int numFeats);

void selectPiece(Quarto* game, int piece);
void deselectPiece(Quarto* game, int piece);

void placePiece(Quarto* game, int piece, int place);
void removePiece(Quarto* game, int piece, int place);

