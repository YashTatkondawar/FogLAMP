#ifndef _JSON_UTILS_H
#define _JSON_UTILS_H
/*
 * FogLAMP utilities functions for handling JSON document
 *
 * Copyright (c) 2018 Dianomic Systems
 *
 * Released under the Apache 2.0 Licence
 *
 * Author: Stefano Simonelli, Massimiliano Pinto
 */

#include<vector>
#include<string>

bool JSONStringToVectorString(std::vector<std::string>& vectorString,
                              const std::string& JSONString,
                              const std::string& Key);

std::string JSONescape(const std::string& subject);
std::string JSONunescape(const std::string& subject);

#endif
