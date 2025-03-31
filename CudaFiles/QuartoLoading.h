#pragma once
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdint.h>

int openSolFile(std::string path, char* boards, int numBoards, int startOffset);
void saveSolutions(std::string path, char* solutions, char* games, int solSize, int numGames, int boardSize);
