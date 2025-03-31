
#include "QuartoHelpers.h"
#include <stdio.h>

void printGame(Quarto* game) {
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
		for (int n = 3; n >=0 ; n--) {
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

void LoadGame(Quarto* game, char* data) {
	int dataPieceIndex = 7;
	int dataPieceMaskShift = 0;

	game->numSelected = 0;
	game->numAvaliable = 0;
	game->numPlaced = 0;

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
				game->numPlaced++;
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
				game->numPlaced++;
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

bool checkWin(Quarto* game) {
	int featList[4];
	//Horizontal I think
	for (int i = 0; i < 16; i += 4) {
		if (checkFeatureList(game->board + i, 4))
			return true;
	}
	//Vertical I think
	for (int i = 0; i < 4; i++) {
		for (int n = 0; n < 4; n++) {
			featList[n] = game->board[i + (4 * n)];
		}
		if (checkFeatureList(featList, 4)) 
			return true;
	}
	//Diagonal
	for (int i = 0; i < 4; i++) {
		featList[i] = game->board[i + (i * 4)];
	}
	if (checkFeatureList(featList, 4))
		return true;
	// Anti Diagonal
	for (int i = 0; i < 4; i++) {
		featList[i] = game->board[i + ((3 - i) * 4)];
	}
	if (checkFeatureList(featList, 4))
		return true;
	return false;
}

bool checkFeatureList(int* feats, int numFeats) {
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

void removeFromArray(char* arr, char val, int len) {
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

void selectPiece(Quarto* game, int piece) {
	// Add piece to end of selected array
	game->selected[game->numSelected] = piece;
	game->numSelected++;
	// Remove piece from avaliable array
	removeFromArray(game->avaliable, piece, 16);
	game->numAvaliable--;
}


void deselectPiece(Quarto* game, int piece) {
	// Add piece to end of avaliable array
	game->avaliable[game->numAvaliable] = piece;
	game->numAvaliable++;
	// Remove piece from selected array
	removeFromArray(game->selected, piece, game->numSelected);
	game->numSelected--;
}

void placePiece(Quarto* game, int piece, int place) {
	if (game->board[place] >= 0) {
		printf("Cannot place piece there\n");
		return;
	}
	game->board[place] = piece;

	removeFromArray(game->selected, piece, game->numSelected);
	game->numSelected--;

	game->numPlaced++;
}

void removePiece(Quarto* game, int piece, int place) {
	game->board[place] = -1;

	game->selected[game->numSelected] = piece;
	game->numSelected++;

	game->numPlaced--;
}
