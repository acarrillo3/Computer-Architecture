"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        
        # RAM
        self.ram = [0] * 256

        # general-purpose registers
        self.reg = [0] * 8
        self.reg[7] = 0xF4    # stack pointer
        self.sp = self.reg[7] # alias for stack pointer

        # internal registers
        self.pc = 0   # program counter
        self.ir = None   # instruction register
        self.mar = None  # memory address register
        self.mdr = None  # memory data register
        self.fl = 0   # flags

        # keep track of whether program is running
        # HALT will set this variable to false
        self.is_running = True

        # define instructions
        
        def hlt():
            self.is_running = False

        def ldi(register, value):
            self.ram[register] = value

        def jmp(register):
            self.pc = register

        def pop(register):
            self.ram[register] = self.ram[self.sp]
            self.sp += 1
            
        def prn(register):
            print(self.ram[register])

        def push(register):
            self.sp -= 1
            self.ram[self.sp] = self.ram[register]

        # hold a mapping of instructions to functions
        self.instructions = dict()
        self.instructions["ADD"] = None
        self.instructions["AND"] = None
        self.instructions["CALL"] = None
        self.instructions["CMP"] = None
        self.instructions["DEC"] = None
        self.instructions["DIV"] = None
        self.instructions[0b00000001] = hlt
        self.instructions["INC"] = None
        self.instructions["INT"] = None
        self.instructions["IRET"] = None
        self.instructions["JEQ"] = None
        self.instructions["JGE"] = None
        self.instructions["JGT"] = None
        self.instructions["JLE"] = None
        self.instructions["JLT"] = None
        self.instructions["JMP"] = jmp
        self.instructions["JNE"] = None
        self.instructions["LD"] = None
        self.instructions[0b10000010] = ldi
        self.instructions["MOD"] = None
        self.instructions[0b10100010] = lambda operand_a, operand_b: self.alu("MUL", operand_a, operand_b)
        self.instructions["NOP"] = None
        self.instructions["NOT"] = None
        self.instructions["OR"] = None
        self.instructions[0b01000110] = pop
        self.instructions["PRA"] = None
        self.instructions[0b01000111] = prn
        self.instructions[0b01000101] = push
        self.instructions["RET"] = None
        self.instructions["SHL"] = None
        self.instructions["SHR"] = None
        self.instructions["ST"] = None
        self.instructions["SUB"] = None
        self.instructions["XOR"] = None

    # retrieve the value stored in the specifed register, and store it in the MDR register
    def ram_read(self, address):

        self.mdr = self.ram[address]

        return self.mdr

    # write the specified value into the specifed register
    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self, program):
        """Load a program into memory."""

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.ram[reg_a] += self.ram[reg_b]
        elif op == "SUB":
            pass
        elif op == "MUL":
            self.ram[reg_a] *= self.ram[reg_b]
        elif op == "DIV":
            pass
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.is_running:

            # store memory address in instruction register
            self.ir = self.ram_read(self.pc)

            # retrieve the next two bytes of data in case they are used as operands
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # determine the number of operands used by the instruction
            first_two_bits = self.ir >> 6
            number_of_operands = first_two_bits

            # execute the instruction
            if self.ir in self.instructions and self.instructions[self.ir] is not None:

                # execute the instructions with any required operands
                if number_of_operands == 0:
                    self.instructions[self.ir]()
                
                elif number_of_operands == 1:
                    self.instructions[self.ir](operand_a)
                
                else:
                    self.instructions[self.ir](operand_a, operand_b)

            else:
                print("Invalid instruction", self.ir)
                pass

            # determine whether the instruction sets the program counter (specified in 5th bit)
            fifth_bit_masked = self.ir & 0b00010000
            modifies_program_counter = fifth_bit_masked >> 4

            if modifies_program_counter:
                pass

            # update program counter to point to the next instruction
            self.pc += number_of_operands + 1