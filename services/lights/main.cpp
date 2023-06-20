#include <iostream>
#include <string>

#include "csv.h"
// #include "test.h"
#include "WS2812Service.hpp"

int main() {
        WS2812Service lightService;
        lightService.run();
        return 0;
}
