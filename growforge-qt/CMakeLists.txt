cmake_minimum_required(VERSION 3.21)

project(GrowForge VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Sql PrintSupport)

qt_standard_project_setup()

# Collect all sources under src/ (CONFIGURE_DEPENDS re-globs on rebuild).
file(GLOB_RECURSE GF_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_SOURCE_DIR}/src/*.cpp"
    "${CMAKE_SOURCE_DIR}/src/*.h"
)

qt_add_executable(growforge
    ${GF_SOURCES}
)

# Make includes work with the directory layout (src/ as a root).
target_include_directories(growforge PRIVATE
    "${CMAKE_SOURCE_DIR}/src"
)

# Embed sample SQL + stylesheet as resources.
qt_add_resources(growforge "appresources"
    PREFIX "/"
    BASE "${CMAKE_SOURCE_DIR}/resources"
    FILES
        "${CMAKE_SOURCE_DIR}/resources/style.qss"
        "${CMAKE_SOURCE_DIR}/resources/sample_data.sql"
        "${CMAKE_SOURCE_DIR}/resources/knowledge.json"
)

target_link_libraries(growforge PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Sql
    Qt6::PrintSupport
)

set_target_properties(growforge PROPERTIES
    WIN32_EXECUTABLE ON
)
