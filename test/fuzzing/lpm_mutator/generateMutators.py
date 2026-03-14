from re import findall, search, MULTILINE
from os import path, makedirs
from glob import glob
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description='Generate C++ mutator factory from proto files')
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, default='factory')
    parser.add_argument('--cpp-file', type=str, default='_mutator_factory.cc')
    parser.add_argument('--header-file', type=str, default='_mutator_factory.h')
    return parser.parse_args()

def parse_proto_file(proto_file):
    # get protocol name out of filename
    protocol = path.splitext(path.basename(proto_file))[0]

    # find all messages using regex
    with open(proto_file, 'r') as f:
        data = f.read()
    message_pattern = r'message\s+(\w+)\s*{'
    messages = findall(message_pattern, data)

    package_pattern = r"^package\s+([\w.]+);"
    package_match = search(package_pattern, data, MULTILINE)
    package_string = package_match.group(1) if package_match else ""

    namespaces = []
    if package_string:
        namespaces = package_string.split(".")

    return namespaces, protocol, messages


def generate_mutator_factory(proto_messages, output_cpp):
    # hardcoded default message
    default_msg = "config_digital_out"
    with open(output_cpp, 'w') as f:
        f.write("""// AUTO-GENERATED FILE - DO NOT EDIT
// Generated from proto files

// Include generated protobuf headers\n""")
        for namespaces, protocol, messages in proto_messages:
            f.write(f'#include "{protocol}.pb.h"\n')
        f.write(f"""

#include "mutator.h"
#include <string>

MyMutatorBase* getMutator(const char* env_var) {{
    if (env_var == nullptr) {{
        return new MyMutator<{default_msg}>();
    }}

    std::string msg(env_var);

""")
        first = True
        all_messages = []

        # generate if chain foreach message
        for namespaces, protocol, messages in proto_messages:
            qual = ""
            for ns in namespaces:
                qual += f"{ns}::"
            for message in messages:
                all_messages.append((protocol, message))

                if first:
                    f.write(f'    if (msg == "{protocol}::{message}") {{\n')
                    first = False
                else:
                    f.write(f'    }} else if (msg == "{protocol}::{message}") {{\n')

                f.write(f'        return new MyMutator<{qual}{message}>();\n')

        f.write(f"""    }} else {{
        // Default fallback
        return new MyMutator<{default_msg}>();
    }}
}}
""")

        # generate comment with all messages
        if all_messages:
            f.write("\n/* Generated Messages:\n")
            for protocol, message in all_messages:
                f.write(f" * {protocol}::{message}\n")
            f.write(" */\n")

def generate_header_file(proto_messages, output_header):
    with open(output_header, 'w') as f:
        f.write("""// AUTO-GENERATED HEADER - DO NOT EDIT
#ifndef MUTATOR_FACTORY_H
#define MUTATOR_FACTORY_H

class MyMutatorBase;



enum messageID {
START = 1,
""")
        for _, protocol, messages in proto_messages:
            if protocol == "helper":
                continue
            for msg in messages:
                f.write(f'{msg.upper()},\n')
        f.write("""
END,
};

messageID getMessageId(std::string env_var);
std::string getMessageString(messageID msg);
// Generated factory function
MyMutatorBase* getMutator(messageID msg);


#endif // MUTATOR_FACTORY_H
""")

def generate_protocol_factory(namespaces, protocol, messages, output_dir):
    filename = f"factory_{protocol}.cc"
    filepath = path.join(output_dir, filename)
    if namespaces:
        qual = "::".join(namespaces) + "::"
    else:
        qual = ""

    with open(filepath, 'w') as f:
        f.write(f'#include "{protocol}.pb.h"\n')
        f.write(f'#include "mutator.h"\n')
        f.write(f'#include "mutator.h"\n')
        f.write(f'#include <map>\n#include <string>\n\n')
        f.write(f'// Protocol: {protocol}\n')
        f.write(f'void register_{protocol}(std::map<messageID, MyMutatorBase* (*)()>& reg) {{\n')

        for msg in messages:
            if msg == "klipperMessage" or msg == "klipperMessageSequence":
                continue
            func_name = f"create_{protocol}_{msg}"
            f.write(f'    reg[messageID::{msg.upper()}] = []() -> MyMutatorBase* {{ return new MyMutator<{qual}{msg}>(); }};\n')

        f.write(f'}}\n')
    return filename

def generate_main_factory(proto_data, output_cpp):
    default_msg = "config_digital_out"

    with open(output_cpp, 'w') as f:
        f.write('#include "mutator.h"\n#include <map>\n#include <string>\n\n')

        # forward declarations
        for _, protocol, _ in proto_data:
            if protocol == "helper":
                continue
            f.write(f'void register_{protocol}(std::map<messageID, MyMutatorBase* (*)()>& reg);\n')

        f.write(f"""
MyMutatorBase* getMutator(messageID msg) {{
    typedef MyMutatorBase* (*CreatorFunc)();
    static std::map<messageID, CreatorFunc> registry;
    static bool initialized = false;

    if (!initialized) {{
""")
        for _, protocol, _ in proto_data:
            if protocol == "helper":
                continue
            f.write(f'        register_{protocol}(registry);\n')
            
        f.write(f"""        initialized = true;
    }}

    if (msg && registry.count(msg)) {{
        return registry[msg]();
    }}
    
    // Default fallback
    return new MyMutator<{default_msg}>();
}}
""")
        f.write(f"""
messageID getMessageId(std::string env_var) {{
""")
        first = True
        for _, protocol, messages in proto_data:
            if protocol == "helper":
                continue
            for msg in messages:
                if first == True:
                    f.write(f'if (env_var == "{msg.upper()}") return messageID::{msg.upper()};\n')
                    first = False
                else:
                    f.write(f'else if (env_var == "{msg.upper()}") return messageID::{msg.upper()};\n')
            
        f.write(f"""
    
    // Default fallback
    return messageID::CONFIG_DIGITAL_OUT;
}}

""")
        f.write(f"""
std::string getMessageString(messageID msg) {{
""")
        first = True
        for _, protocol, messages in proto_data:
            if protocol == "helper":
                continue
            for msg in messages:
                if first == True:
                    f.write(f'if (msg == messageID::{msg.upper()}) return "{msg.upper()}";\n')
                    first = False
                else:
                    f.write(f'else if (msg == messageID::{msg.upper()}) return "{msg.upper()}";\n')
            
        f.write(f"""
    
    // Default fallback
    return "IDENTIFY";
}}

""")

def main():
    #parse arguments
    args = parse_args()

    # check paths
    if not path.exists(args.input):
        print(f"Input directory '{args.input}' doesn't exist")
        return
    if not path.exists(args.output):
        makedirs(args.output)

    # find .proto files in input dir
    # exclude headers from factory generation because they do not include ipdl protocol messages
    all_proto_files = glob(path.join(args.input, "**/*.proto"), recursive=True)
    proto_header_files = glob(path.join(args.input, "**/*.h.proto"), recursive=True)
    proto_files = list(set(all_proto_files) - set(proto_header_files))
    proto_files.sort()

    if not proto_files:
        print(f"No .proto files found in input directory")
        return

    # parse all protocol + message names
    proto_messages = []
    protocol_count = 0
    msg_count = 0
    for file in proto_files:
        try:
            namespaces, protocol, messages = parse_proto_file(file)
            protocol_count += 1
            msg_count += len(messages)
            proto_messages.append((namespaces, protocol, messages))
            if protocol == "helper":
                continue
            generate_protocol_factory(namespaces, protocol, messages, args.output)
            print(f"Found {len(messages)} messages in {protocol} and generated factory")

        except Exception as e:
            print(f"Error parsing {file}")

    if msg_count == 0:
        print("No messages found")
        return

    # generate cpp code
    output_cpp = path.join(args.output, args.cpp_file)
    output_header = path.join(args.output, args.header_file)
    #generate_mutator_factory(proto_messages, output_cpp)
    generate_main_factory(proto_messages, output_cpp)
    generate_header_file(proto_messages, output_header)

    print("\nDone!")
    print(f"Generated: {output_cpp}")
    print(f"Generated: {output_header}")
    print(f"Added {msg_count} message types from {protocol_count} proto files")

if __name__ == "__main__":
    main()
