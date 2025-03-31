#include "QuartoHelpers.h"
#include "QuartoLoading.h"
#include "quartoCuda.cuh"
#include <chrono>

//Timer made by the lovely GPT

class Timer {
public:
	Timer() : start_time(std::chrono::high_resolution_clock::now()) {}

	void reset() {
		start_time = std::chrono::high_resolution_clock::now();
	}

	void elapsed() const {
		auto end_time = std::chrono::high_resolution_clock::now();
		auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

		long long milliseconds = duration.count();
		long long hours = milliseconds / 3600000;
		milliseconds %= 3600000;
		long long minutes = milliseconds / 60000;
		milliseconds %= 60000;
		long long seconds = milliseconds / 1000;
		milliseconds %= 1000;

		std::cout << "Elapsed time: " << hours << "h "
			<< minutes << "m " << seconds << "s "
			<< milliseconds << "ms" << std::endl;
	}

private:
	std::chrono::high_resolution_clock::time_point start_time;
};


int solveGame(
	Quarto* game,
	char* sol,
	int solIndex,
	int depth,
	bool turn,
	bool placingPiece
);
void copyStr(char* srcStr, char* dstStr);

using namespace std;

int main() {
	Timer timer;

	string filePath = "S:/QuartoStates/depth6full.txt";
	string dstPath = "S:/QuartoStates/depth6_5mil.txt";
	//string filePath = "S:/QuartoStates/depth6_6mil_filtered.txt";
	
	//string filePath = "S:/QuartoStates/depth6filtered.txt";
	//string filePath = "testDepth7.txt";
	const int startOffset = 0;
	const int gamesToLoad = 10;
	const int gameSize = 10;
	const int solutionSize = 24; // Max number of chars in a solution, plus null termination

	char *loadedGames = static_cast<char*>(malloc(gameSize * gamesToLoad * sizeof(char)));
	char *solutions   = static_cast<char*>(malloc(solutionSize * gamesToLoad * sizeof(char)));

	cout << "Loading Games" << endl;
	int numGamesLoaded = openSolFile(filePath, loadedGames, gamesToLoad, startOffset);
	printf("Loaded %d games!\n\n", numGamesLoaded);

	// Cuda Solution
	solveGamesCuda(loadedGames, solutions, numGamesLoaded, solutionSize);

	//Serial Solution
	Quarto game;
	//for (int i = 0; i < gamesToLoad; i++) {
	//	LoadGame(&game, loadedGames + (i * gameSize));
	//	//printGame(&game);
	//	solveGame(&game, solutions + i * solutionSize, 0, 0, true, false);
	//	
	//	printf("Solved %d\n", i);
	//}


	// Testing times at different depths
	/*LoadGame(&game, loadedGames);
	selectPiece(&game, 2);
	placePiece(&game, 2, 12);
	cout << checkWin(&game) << endl;

	selectPiece(&game, 4);
	placePiece(&game, 4, 5);
	cout << checkWin(&game) << endl;

	selectPiece(&game, 6);
	placePiece(&game, 6, 7);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 12);
	placePiece(&game, 12, 8);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 1);
	placePiece(&game, 1, 9);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 8);
	placePiece(&game, 8, 3);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 9);
	placePiece(&game, 9, 14);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 13);
	placePiece(&game, 13, 13);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 11);
	placePiece(&game, 11, 4);
	cout << checkWin(&game) << endl;*/

	/*selectPiece(&game, 3);
	placePiece(&game, 3, 1);
	cout << checkWin(&game) << endl;*/

	printGame(&game);
	printf("\n\n");

	solveGame(&game, solutions, 0, 0, true, false);
	printf("Solution: ");
	printf(solutions);

	printf("\n\n");


	//saveSolutions(dstPath, solutions, loadedGames, solutionSize, numGamesLoaded, gameSize);
	//saveSolutions("cpuDepth6.txt", solutions, loadedGames, solutionSize, gamesToLoad, gameSize);

	free(loadedGames);
	free(solutions);


	timer.elapsed();

	return 0;
}

// Copies null terminated string into another string
void copyStr(char* srcStr, char* dstStr) {
	for (int i = 0; i < 1000; i++) { // dummy counter, just to prevent an infinite loop
		dstStr[i] = srcStr[i];
		if (srcStr[i] == '\0')
			return;
	}
}

int solveGame(
	Quarto* game,
	char* sol,
	int solIndex,
	int depth,
	bool turn,
	bool placingPiece
) {
	bool isFinal = checkWin(game);

	// ===== NEXT logic =========
	if (isFinal) {
		sol[solIndex + 1] = '\0'; // Null termination
		sol[solIndex] = (char)(1 + 49); //arbitrary ascii offset
		return 1;
	}
	if (game->numPlaced >= 16) {
		sol[solIndex + 1] = '\0'; // Null termination
		sol[solIndex] = (char)(0 + 49); //arbitrary ascii offset
		return 0;
	}

	// ===== PREV logic =========
	//if (isFinal || game->numAvaliable <= 0) {
	//	int score = 0;
	//	if (isFinal) {
	//		if (turn) { score = 1; }
	//		else { score = -1; }
	//	}

	//	sol[solIndex + 1] = '\0'; // Null termination
	//	sol[solIndex] = (char)(score + 49); //arbitrary ascii offset
	//	return score;
	//}

	int bestScore = -2;
	int score;
	char bestSol[22];

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
			placePiece(game, currPiece, avalSquares[i]);
			score = solveGame(game, sol, solIndex + 1, depth + 1, turn, false);
			removePiece(game, currPiece, avalSquares[i]);

			// ===== PREV logic =======
			/*if (!turn)
				score *= -1;*/

			if (score > bestScore) {
				bestScore = score;
				bestSquare = avalSquares[i];
				copyStr(sol + solIndex + 1, bestSol);
			}
			if (bestScore > 0) {
				break;
			}
		}
		if (bestScore < -1) { // should only occur in error, but there are error boards
			copyStr("XxX", sol + solIndex);
			return -2;
		}
		copyStr(bestSol, sol + solIndex + 1);
		int squareIndex = ((bestSquare % 4) << 2) + (bestSquare / 4);
		sol[solIndex] = (char)(squareIndex + 64);
		return bestScore;
		
	}
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
			selectPiece(game, piece);
			score = solveGame(game, sol, solIndex + 1, depth + 1, !turn, true);
			deselectPiece(game, piece);

			// ===== NEXT logic =======
			score *= -1;

			// ===== PREV logic =======
			/*if (turn)
				score *= -1;*/

			if (score > bestScore) {
				bestScore = score;
				bestPiece = piece;
				copyStr(sol + solIndex + 1, bestSol);
			}
			if (bestScore > 0) {
				break;
			}

		}
		if (bestScore < -1) { // should only occur in error, but there are error boards
			copyStr("XxX", sol + solIndex);
			return -2;
		}
		copyStr(bestSol, sol + solIndex + 1);
		sol[solIndex] = (char)(bestPiece + 64);
		return bestScore;
	}
}


