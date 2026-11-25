import sys
import os

# Lookup tables for C-instructions
COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

DEST_TABLE = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011",
    "A":   "100", "AM":  "101", "AD":  "110", "AMD": "111",
}

JUMP_TABLE = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

def init_symbol_table():
    symbols = {
        "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576
    }
    for i in range(16):
        symbols[f"R{i}"] = i
    return symbols

def clean_lines(raw_lines):
    cleaned = []
    for line in raw_lines:
        # Remove comments and whitespace
        line = line.split("//")[0].strip().replace(" ", "")
        if line:
            cleaned.append(line)
    return cleaned

def assemble(asm_path):
    with open(asm_path, "r") as f:
        lines = clean_lines(f.readlines())

    symbols = init_symbol_table()

    # First Pass: Record (LABEL) ROM addresses
    rom_address = 0
    instructions = []
    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbols[label] = rom_address
        else:
            instructions.append(line)
            rom_address += 1

    # Second Pass: Translate instructions to 16-bit binary
    next_var_address = 16
    binary_output = []

    for inst in instructions:
        if inst.startswith("@"):
            # A-Instruction
            symbol = inst[1:]
            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_var_address
                    next_var_address += 1
                address = symbols[symbol]
            binary_output.append(f"0{address:015b}")
        else:
            # C-Instruction: [dest=]comp[;jump]
            dest, rest = ("", inst)
            if "=" in inst:
                dest, rest = inst.split("=", 1)
            comp, jump = (rest, "")
            if ";" in rest:
                comp, jump = rest.split(";", 1)

            binary_line = f"111{COMP_TABLE[comp]}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"
            binary_output.append(binary_line)

    # Write output to .hack file
    out_path = os.path.splitext(asm_path)[0] + ".hack"
    with open(out_path, "w") as f:
        f.write("\n".join(binary_output) + "\n")

    print(f"Success! Encoded {len(binary_output)} instructions -> {out_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <program.asm>")
        sys.exit(1)
    assemble(sys.argv[1])
