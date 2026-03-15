#!/bin/bash

AFL_CUSTOM_MUTATOR_LIBRARY=./test/fuzzing/lpm_mutator/mutator.so
AFL_CUSTOM_MUTATOR_ONLY=1
AFL_DISBALE_TRIM=1
AFL_POST_PROCESS_KEEP_ORIGINAL=1    # To signal AFL++ to save the protobuf formatted input instead of the post-process klipper format into to corpora

SET_TARGET=MULTIMESSAGE
AFL_DEBUG=1
DEBUG=1



afl-fuzz -i fuzz/in/ -o fuzz/out3 ./out/klipper.elf
