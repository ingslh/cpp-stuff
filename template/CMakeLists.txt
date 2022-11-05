cmake_minimum_required(VERSION 3.0)

if(APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "Minimum OS X deployment version")
endif()

project(cpp-stuff)
	
set(CMAKE_CXX_STANDARD 14)

set(PROJECT_NAME cpp-stuff)

set (EFFECT_TOOL_FILES
    src/main.cpp
    #...
	)

source_group(effect_tool FILES ${EFFECT_TOOL_FILES}) 

# Find Qt
if(WIN32)
  set(Qt5_ROOT_DIR "c:/Qt/Qt5.12.7/5.12.7/msvc2017_64")
elseif(APPLE)
  set(Qt5_ROOT_DIR "$ENV{HOME}/Qt5.12.7/5.12.7/clang_64")
elseif(UNIX)
  set(Qt5_ROOT_DIR "/home/wonder/Qt5.12.7/5.12.7/gcc_64")
endif()
set(Qt5_DIR "${Qt5_ROOT_DIR}/lib/cmake/Qt5")
find_package(Qt5 COMPONENTS Core Widgets Gui LinguistTools Xml REQUIRED)

#http://doc.qt.io/qt-5/cmake-manual.html

set(WES_DIR ${PROJECT_SOURCE_DIR}/../WES)

set(CMAKE_INCLUDE_CURRENT_DIR ON)  
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

set(TS_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(TS_FILES
    "${TS_DIR}/${PROJECT_NAME}_zh_CN.ts"
)

find_program(LUPDATE_EXECUTABLE lupdate PATHS ${Qt5_ROOT_DIR}/bin/)
find_program(LRELEASE_EXECUTABLE lrelease PATHS ${Qt5_ROOT_DIR}/bin/)

foreach(_ts_file ${TS_FILES})
    execute_process(
        COMMAND ${LUPDATE_EXECUTABLE} -recursive ${CMAKE_SOURCE_DIR} -ts ${_ts_file})
    execute_process(
        COMMAND ${LRELEASE_EXECUTABLE} ${_ts_file})
endforeach()

IF(TS_FILES)
	QT5_ADD_TRANSLATION(QM_FILES ${TS_FILES})	
	SOURCE_GROUP("Translation Files" FILES ${TS_FILES})
ENDIF()

IF(QRC_FILE)
	#QT5_ADD_RESOURCES(RES_FILES ${QRC_FILE})
	SOURCE_GROUP("Resource Files" FILES ${QRC_FILE})
ENDIF()

if(WIN32)
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Zi")
  set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /DEBUG /OPT:REF /OPT:ICF /SUBSYSTEM:WINDOWS /entry:mainCRTStartup")
endif()

if(UNIX)
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)
  set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
  if(NOT APPLE)
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
  else()
    cmake_policy(SET CMP0068 OLD)
    set(CMAKE_MACOSX_RPATH ON)
    set(CMAKE_INSTALL_RPATH "@executable_path")
    #set(CMAKE_INSTALL_NAME_DIR "@loader_path/../lib")
  endif()
endif()

if(UNIX)
  set(CMAKE_INSTALL_RPATH "${Qt5_DIR}/../..;${CMAKE_INSTALL_RPATH}")
endif()

if(CMAKE_SIZEOF_VOID_P MATCHES 8)
	set(PROJECT_ARCH "x64")
else(CMAKE_SIZEOF_VOID_P MATCHES 4)
	set(PROJECT_ARCH "Win32")
endif()

if(APPLE)
  set(CONFIG_TYPE $(CONFIGURATION))
else()
  set(CONFIG_TYPE ${CMAKE_CFG_INTDIR})
endif()
set(TARGET_TRIPLE_CONFIG ${CMAKE_SYSTEM_NAME}-${PROJECT_ARCH}-${CONFIG_TYPE})	

set(_WES_PACKAGE_ROOT ${PROJECT_SOURCE_DIR}/../../wes-package/${TARGET_TRIPLE_CONFIG})
set(_INTERNAL_ROOT ${_WES_PACKAGE_ROOT}/internal)
set(_3RDPARTY_ROOT ${_INTERNAL_ROOT}/wes-3rdparty)

set(CMAKE_INSTALL_PREFIX ${_WES_PACKAGE_ROOT})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_INSTALL_PREFIX}/bin)
set(CMAKE_PDB_OUTPUT_DIRECTORY ${CMAKE_INSTALL_PREFIX}/pdb)

foreach(config ${CMAKE_CONFIGURATION_TYPES})
  string(TOUPPER "${config}" config_uc)
  foreach(type ARCHIVE LIBRARY RUNTIME PDB)
    set(CMAKE_${type}_OUTPUT_DIRECTORY_${config_uc}
        ${CMAKE_${type}_OUTPUT_DIRECTORY})
  endforeach()
  unset(config_uc)
endforeach()

SET(INCLUDE_DIRECTORIES include src/mainwindow src/preview_window src/timeline src/timeline_media src/effect_editor src/effect_tool src/contents src/commands src/tool src/content_preview src/graph_editor ${_WES_PACKAGE_ROOT}/include ${_3RDPARTY_ROOT}/include src/zlib-1.2.11 )
SET(LIBS_DIRECTORIES ${_WES_PACKAGE_ROOT}/lib ${_3RDPARTY_ROOT}/lib)
list(APPEND INCLUDE_DIRECTORIES ${_3RDPARTY_ROOT})
list(APPEND INCLUDE_DIRECTORIES ${_INTERNAL_ROOT}/wes-3rdparty/xpack)
SOURCE_GROUP("Generated Files" FILES ${QT_UI_FILES} ${RES_FILES} ${QM_FILES})

link_directories(${LIBS_DIRECTORIES})

option(EXPORT_NLE "can export nle template." ON)

if (EXPORT_NLE)
else(EXPORT_NLE)
add_definitions(-DSUPPORT_WES)
endif(EXPORT_NLE)

configure_file(${PROJECT_SOURCE_DIR}/../../app_version.h.in app_version.h)

set(effect_app_WINRC effect_app.rc)
set_property(SOURCE effect_app.rc APPEND PROPERTY OBJECT_DEPENDS ${PROJECT_SOURCE_DIR}/resource/Launch_Effect.ico)
add_executable(${EFFECT_TOOL_NAME} WIN32 ${effect_app_WINRC} ${QT_UI_FILES} ${EFFECT_TOOL_FILES} ${PREVIEW_WINDOW_FILES}  ${MAINWINDOW_FILES} ${CONTENTS_FILES} ${CONTENT_PREVIEW} ${EFFECT_EDITOR_FILES} ${TIMELINE_FILES} ${TIMELINE_MEDIA_FILES} ${COMMANDS_FILES} ${EFFECT_VIEW_FILES} ${GRAPH_EDITOR} ${TOOL_FILES} ${SRC_FILES} ${CONTENT_LIBRARY} ${RESOURCE_FILE} ${QRC_FILE} ${RES_FILES} ${VERSION_RC} ${TS_FILES} ${QM_FILES})

SET_TARGET_PROPERTIES(${EFFECT_TOOL_NAME} PROPERTIES LINK_FLAGS  "/MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\"")

target_include_directories(${EFFECT_TOOL_NAME} PRIVATE ${INCLUDE_DIRECTORIES})

target_compile_definitions(${EFFECT_TOOL_NAME} PRIVATE QUAZIP_BUILD)
target_compile_definitions(${EFFECT_TOOL_NAME} PRIVATE GLEW_STATIC)
target_compile_definitions(${EFFECT_TOOL_NAME} PRIVATE USING_QT_OPENGL_CONTEXT)

if(WIN32)
  target_compile_definitions(${EFFECT_TOOL_NAME} PUBLIC _CRT_SECURE_NO_DEPRECATE _CRT_SECURE_NO_WARNINGS)
else()
  target_compile_options(${EFFECT_TOOL_NAME} PUBLIC -std=c++14 -msse4)
  target_compile_definitions(${EFFECT_TOOL_NAME} PUBLIC _FILE_OFFSET_BITS=64)
  target_compile_definitions(${EFFECT_TOOL_NAME} PRIVATE USING_OPENGL_RENDER=1 USING_QT_OPENGL_CONTEXT=1)
endif()

target_link_libraries(${EFFECT_TOOL_NAME} Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Xml)
target_link_libraries(${EFFECT_TOOL_NAME} template tlb core avcore resource service libservice-player)


if(WIN32)
  target_link_libraries(${EFFECT_TOOL_NAME} version)
endif()

set_property(TARGET ${EFFECT_TOOL_NAME} PROPERTY QT5_NO_LINK_QTMAIN ON)

if(MSVC)    
  add_definitions(/W2 /GR)
else()
  add_definitions(-fexceptions -frtti)
endif()
