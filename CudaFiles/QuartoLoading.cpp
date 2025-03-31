#include "QuartoLoading.h"

using namespace std;

void boardHashToChars(int64_t boardHash, char* board, int charsPerBoard) {
	for (int i = charsPerBoard - 1; i >= 0; i--) {
		board[i] = char(boardHash & 255);
		boardHash = boardHash >> 8;
	}
}

int openSolFile(string path, char* boards, int numBoards, int startOffset) {

	string line;
	ifstream file(path);

	int boardSize = 10; // Number of chars per boards
	int numLoaded = 0;

	int64_t boardHash;
	string solution;

	for (int i = 0; i < numBoards; i++) {	
		if (getline(file, line)) {
			if (startOffset > 0) {
				startOffset--;
				i--;
			}
			else {
				stringstream ss(line);

				ss >> boardHash;
				ss >> solution;
				if (!solution.empty() && solution[0] == ',') {
					solution = solution.substr(1);
				}

				boardHashToChars(boardHash, boards + (boardSize * i), boardSize);

				numLoaded++;
			}
		}
		else {
			break;
		}
	}

	file.close();

	return numLoaded;
}

int64_t hashGame(char* game, int gameSize) {
	int64_t hash = 0;
	for (int i = 0; i < gameSize; i++) {
		hash = hash << 8;
		hash += static_cast<uint8_t>(game[i]);
	}
	return hash;
}

void saveSolutions(
	std::string path, 
	char* solutions, 
	char* games, 
	int solSize, 
	int numGames,
	int boardSize
) {
	ofstream file(path);

	for (int i = 0; i < numGames; i++) {
		bool isValidSolution = false;
		int64_t hash = hashGame(games + boardSize * i, boardSize);
		file << to_string(hash);
		file << ",";
		// A solution is only valid if it's null terminated within 23 chars
		for (int n = 0; n < 24;n++) {
			if (solutions[n + i * solSize] == '\0') {
				isValidSolution = true;
				break;
			}
		}
		if (isValidSolution) {
			file << solutions + i * solSize;
		}
		else {
			file << "-";
		}
		file << "\n";
	}

	file.close();
}