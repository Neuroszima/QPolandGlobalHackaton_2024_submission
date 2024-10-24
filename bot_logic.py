from math import log2, floor

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer.backends import AerSimulator
from qiskit.circuit import ControlledGate
from qiskit.circuit.library.standard_gates import XGate
from qiskit.circuit.quantumregister import Qubit

# from qiskit.circuit.library import GroverOperator

from matplotlib import pyplot as plt

MOVES_LIST_TYPEHINT = list[list[int, int, int, int]] | list[tuple[int, int, int, int]]
ASSIGNED_STATES_TYPEHINT = dict[str, list]
BOARD_TYPEHINT = list[list[str]]


class QuantumBot:
    ALLOWED_CONDITION_COUNT = [1, 2]  # 3rd in baking

    def __init__(self, number_of_conditions: int):  # condition_map: dict
        """
        This class serves as the means of gauging probabilities of certain available moves the bot can make

        It is based on grover algorithm -> phase kickback + idea of "state probability inversion over the mean"

        several registers are used to tie different sub-circuits together to create functioning algorithm
        There is also a system of "conditions" that flags states that are more incentivized to be picked by the bot
        An example condition might be "beating enemy checker", "prevent overextending" and so on

        these states will then be flipped; there is also a need to get correct number of good conditions
        these conditions will be added in "quantum accumulator", that then will be used in state flagging on certain
        condition (for example -> mark all the states that got at least one condition right)
        """
        if not number_of_conditions in self.ALLOWED_CONDITION_COUNT:
            raise ValueError(f"number_of_conditions should be one of: {self.ALLOWED_CONDITION_COUNT}")
        self.master_circuit: QuantumCircuit | None = None
        self.board_moves_qbit_register: QuantumRegister | None = None
        self.ancilla_register: QuantumRegister | None = None
        self.quantum_adder_register: QuantumRegister | None = None
        self.condition_register: QuantumRegister | None = None
        self.results_register: ClassicalRegister | None = None
        self.number_of_conditions = number_of_conditions
        # self.condition_map = condition_map
        self.valid_moves_with_flags: dict | None = None
        self.current_job_shots: int | None = None
        self.counts: dict | None = None

        self.verbose = True

    @staticmethod
    def q_minimal_board_move_alloc(valid_moves_count: int):
        return floor(log2(valid_moves_count))+1

    @staticmethod
    def _check_if_out_of_border(col, row):
        """check if board position is actually a valid board position"""
        if 0 <= row <= 7:
            if 0 <= col <= 7:
                return False
        return True

    def _present_full_state(self, state: str):
        "|" + f"{state}".zfill(len(self.board_moves_qbit_register)) + ">"

    def q_allocate_registers(self, valid_moves_count):
        """creates registers for future purposes"""
        moves_q_alloc = self.q_minimal_board_move_alloc(valid_moves_count)
        self.board_moves_qbit_register = QuantumRegister(moves_q_alloc + self.number_of_conditions + 1, name="board")
        if self.number_of_conditions < 4:  # up to 3?
            self.quantum_adder_register = QuantumRegister(2, name="add")  # quantum counting up to 3
        else:
            self.quantum_adder_register = QuantumRegister(3, name="add")  # quantum counting up to 7

        self.results_register = ClassicalRegister(moves_q_alloc + self.number_of_conditions + 1, name="meas.")
        self.ancilla_register = QuantumRegister(1, name="anc")  # extra qbit for Z-flip action
        self.condition_register = QuantumRegister(self.number_of_conditions, name="condi")

    def q_initialize(self):
        """
        create master circuit that will get all the sub-circuits composed into
        all the compositions that will further take place should happen as in_place=True
        """
        self.master_circuit = QuantumCircuit(
            self.board_moves_qbit_register, self.condition_register, self.quantum_adder_register,
            self.ancilla_register, self.results_register
        )

        self.master_circuit.h(self.board_moves_qbit_register)

    def assign_valid_board_moves_to_q_states(self, valid_moves_list: MOVES_LIST_TYPEHINT) -> ASSIGNED_STATES_TYPEHINT:
        """
        assign quantum state equivalent to the board move that was passed as valid
        probabilities are

        :returns: dictionairy of the structure:
            key: [move, state_1_flag, state_2_flag, probability (0)]

        """
        # move: (start_row, start_col, fin_row, fin_col)
        states_assigned = dict()
        for index, move in enumerate(valid_moves_list):
            # state = "|" + f"{bin(index)[2:]}".zfill(len(self.board_moves_qbit_register)) + ">"
            state = f"{bin(index)[2:]}".zfill(self.q_minimal_board_move_alloc(len(valid_moves_list)))
            # for example, following could result in:
            # { ...
            #       "000" : [(3, 4, 3, 1), 0, 0, 0],
            # ... }
            # translates to:
            # "partial_q_state": [
            #       corresponding_valid_move, condition_1_placeholder (0),
            #       condition_2_placeholder (0), 0_probability (placeholder)]
            states_assigned[state] = [move, *[0 for _ in range(self.number_of_conditions)], 0]

        return states_assigned

    def condition_piece_shielded(
            self, board: BOARD_TYPEHINT, assigned_states_to_fill: ASSIGNED_STATES_TYPEHINT,
            current_player: str, condition_num=1):
        """
        This condition aims at preventing overextending of the board pieces.
        This in turn means that a piece, after finished move, will have the piece of the same color on one
        of its sides, behind its back. This prevents beating pieces of its color

        :param condition_num: this param controls which condition should be marked
            from method above, if condition is true then "1" means -> mark condition_1_placeholder as "1"
        """
        # move: (start_row, start_col, fin_row, fin_col)

        for state in assigned_states_to_fill:
            move = assigned_states_to_fill[state][0]
            fin_col, fin_row = move[3], move[2]
            start_col, start_row = move[1], move[0]
            # following are always +/- 1, we want "1 to the side, and 1 row BEHIND!"
            # "BEHIND" -> making this color agnostic, from both perspectives
            direction_col = int((fin_col - start_col) / (fin_col - start_col))
            direction_row = int((fin_row - start_row) / (fin_row - start_row))
            test_col, test_row = [fin_col + direction_col, start_row - direction_row]  # col, row
            # conditions
            if self._check_if_out_of_border(test_col, test_row):
                assigned_states_to_fill[state][condition_num] = 1
                continue
            if board[test_row][test_col] == current_player:
                assigned_states_to_fill[state][condition_num] = 1

        return assigned_states_to_fill

    def condition_moves_to_be_beaten(
            self, board: BOARD_TYPEHINT, assigned_states_to_fill: ASSIGNED_STATES_TYPEHINT,
            enemy_player: str, condition_num=2):
        """
        This condition checks, if after the move, our piece moved would get beaten

        Since this test looks for potentially bad moves, we can "invert the logic" and always mark "1",
        unless the situation finds the move to not be worth it. Then it will stay as "0"
        """

        # move: (start_row, start_col, fin_row, fin_col)
        for state in assigned_states_to_fill:
            move = assigned_states_to_fill[state][0]
            fin_col, fin_row = move[3], move[2]
            start_col, start_row = move[1], move[0]
            direction_col = int((fin_col - start_col) / (fin_col - start_col))
            direction_row = int((fin_row - start_row) / (fin_row - start_row))
            test_col_1, test_row_1 = fin_col - direction_col, fin_row + direction_row  # perpendicular, higher
            test_col_2, test_row_2 = fin_col + direction_col, fin_row + direction_row  # in the direction, higher
            # conditions
            print(test_col_1, test_row_1)
            print(test_col_2, test_row_2)
            if not self._check_if_out_of_border(test_col_1, test_row_1):  # perpendicular check

                if board[test_row_1][test_col_1] == enemy_player:
                    # lower, perpendicular out of board?
                    if not self._check_if_out_of_border(test_col_2, fin_row - direction_col):
                        # can this enemy really jump over on the perpendicular lower empty field?
                        if board[fin_row - direction_col][test_col_2] == " ":
                            # assigned_states_to_fill[state][condition_num] = 0
                            continue

            if not self._check_if_out_of_border(test_col_2, test_row_2):  # check "in the direction"
                if board[test_row_1][test_col_2] == enemy_player:
                    # lower, in the direction we cane from with the piece is always empty
                    # eather through beating or through just piece moving out
                    # assigned_states_to_fill[state][condition_num] = 0
                    continue
            assigned_states_to_fill[state][condition_num] = 1  # it is an ok move -> approved to move like that

        return assigned_states_to_fill

    def q_condition_check(self, prepared_assigned_states: ASSIGNED_STATES_TYPEHINT) -> QuantumCircuit:
        """
        triggers condition flags to be passed into quantum condition register, per state (which in turn is - per
        possible move)

        takes -> board moves (states) register
        outputs -> condition register
        """
        check_circuit = QuantumCircuit(self.board_moves_qbit_register, self.condition_register)

        # we operate on extend board_move_register, with the "control bits" expanded by num_conditions ,
        # then we control qbits: (last, last-1, ...) in quantum state register

        # this way we artificially pump omega -> total number of quantum solutions, by 2x per additional qbit
        # we however ONLY mark one configuration of the last bits, which make it cut out into omega/2^(num_conditions)
        # this all in turn will dilute grover operator

        # we do all this to not overshoot with too many grover diffusion iterations, as when we diffuse too much,
        # probabilities start to diminish, and then after even more time, the BAD-move quantum states will start to
        # be brought up by grover's algorithm... and this repeats "ad infinum"
        CNXGate: ControlledGate = XGate().control(len(self.board_moves_qbit_register))

        for state in prepared_assigned_states:
            check_circuit.barrier()
            for flag_index, flag in enumerate(prepared_assigned_states[state][1:-1]):  # absolut last elem. is "prob. placeholder"
                if flag:
                    for invert_index, c in enumerate(reversed(state)):
                        if c == "0":
                            print(state)
                            print(invert_index)
                            print(prepared_assigned_states)
                            check_circuit.append(XGate(), [self.board_moves_qbit_register[invert_index]])
                    check_circuit.append(CNXGate, [
                        *self.board_moves_qbit_register,
                        self.condition_register[flag_index]
                    ])
                    for invert_index, c in enumerate(reversed(state)):
                        if c == "0":
                            check_circuit.append(XGate(), [self.board_moves_qbit_register[invert_index]])
        self.__draw_circuit(check_circuit)

        return check_circuit

    def q_adder(self) -> QuantumCircuit:
        """
        Prepare adder pyramid for favourable condition counting and accumulation
        This piece will add all the conditions that are good, to move into accumulator

        takes -> condition register
        outputs -> adder register
        """

        adder_circuit = QuantumCircuit(self.condition_register, self.quantum_adder_register)

        # controlled gate dict will serve as "library of controlled-XGates"
        # we need this to dynamically allocate correct number of additions to be performed, based
        # on total number of "favourable conditions"
        controlled_gate_dict = dict()
        for index, _ in enumerate(self.quantum_adder_register):
            controlled_gate_dict[index+1] = XGate().control(index+1)

        all_gates = []
        for qbit_index, qbit in enumerate(self.condition_register):

            # there needs to be a gate pyramid created for each condition qbit, with control complexity
            # that match floor(log2(qbit_index)) of exact qbit in a series to be added.

            temp = floor(int(log2(qbit_index + 1))) + 1

            # this prepares entire "instruction pack" on how to correctly add every subsequent marked condition
            gates_for_qbit = []
            while temp > 0:
                gates_for_qbit.append([qbit, controlled_gate_dict[temp]])
                temp -= 1
            all_gates.extend(gates_for_qbit)

        for instruction_pack in all_gates:
            # here we add gates with control and make a part of the circuit
            # based on target that was passed in previous step

            qbit: Qubit = instruction_pack[0]
            gate: ControlledGate = instruction_pack[1]

            control_adder_qbits_count = target_adder_bit = gate.num_qubits - 2
            if control_adder_qbits_count == 0:
                control_adder_qbits = []
            else:
                control_adder_qbits = [self.quantum_adder_register[i] for i in range(control_adder_qbits_count)]
            adder_circuit.append(
                gate, [qbit, *control_adder_qbits, self.quantum_adder_register[target_adder_bit]]
            )
        self.__draw_circuit(adder_circuit)

        return adder_circuit

    def q_adder_check(self, number_to_diffuse_over: int) -> QuantumCircuit:
        """
        pick correct number and make it a condition over accumulator

        takes -> adder register
        outputs -> ancilla register
        """
        possible_numbers = [*range(2**(len(self.quantum_adder_register) + 1))]
        adder_len = len(self.quantum_adder_register)
        if not number_to_diffuse_over in possible_numbers:
            raise ValueError("wrong number")

        C3XGate: ControlledGate = XGate().control(3)
        C2XGate: ControlledGate = XGate().control(2)
        adder_check_circuit = QuantumCircuit(self.quantum_adder_register, self.ancilla_register)

        binstr = bin(number_to_diffuse_over)[2:].zfill(adder_len)
        for index, c in enumerate(reversed(binstr)):
            if c == "0":
                adder_check_circuit.x(self.quantum_adder_register[index])

        if adder_len == 3:
            adder_check_circuit.append(C3XGate, [*self.quantum_adder_register, *self.ancilla_register])
        elif adder_len == 2:
            adder_check_circuit.append(C2XGate, [*self.quantum_adder_register, *self.ancilla_register])
        self.__draw_circuit(adder_check_circuit)

        return adder_check_circuit

    def __grover_diffusion(self) -> QuantumCircuit:
        """
        flags all the states that present themselves to solve the equation, inverting their state for "-"
        n-controlled z-gate in this stage is not supported by qiskit, so it was swapped into x-gate based
        diffusion mechanism
        takes and outputs -> board moves (states) register
        """

        grover_diffusion_circuit = QuantumCircuit(self.board_moves_qbit_register)
        x_gate_controlled = XGate().control(num_ctrl_qubits=len(self.board_moves_qbit_register)-1)

        grover_diffusion_circuit.h(self.board_moves_qbit_register)
        grover_diffusion_circuit.x(self.board_moves_qbit_register)

        # I had troubles with qiskit recognizing n-(c)ZGate, this construct seems to work as an equivalent
        grover_diffusion_circuit.h(self.board_moves_qbit_register[-1])
        grover_diffusion_circuit.append(x_gate_controlled, [*self.board_moves_qbit_register])
        grover_diffusion_circuit.h(self.board_moves_qbit_register[-1])

        grover_diffusion_circuit.x(self.board_moves_qbit_register)
        grover_diffusion_circuit.h(self.board_moves_qbit_register)

        return grover_diffusion_circuit

    def q_prepare_iteration(self, iteration_num: int):
        """prepares entire diffusion procedure"""
        possible_numbers = [*range(2**(len(self.quantum_adder_register)))]
        diffusion = self.__grover_diffusion()

        condition_check_circuit = self.q_condition_check(self.valid_moves_with_flags)
        adder_circuit = self.q_adder()

        adder_check_circuits: list[QuantumCircuit] = []
        for i in possible_numbers[iteration_num:]:
            adder_check_circuits.append(self.q_adder_check(i))

        # assembly
        self.master_circuit.compose(
            condition_check_circuit, [*self.board_moves_qbit_register, *self.condition_register], inplace=True)
        self.master_circuit.barrier()
        # self.__draw_master_circuit()
        self.master_circuit.compose(
            adder_circuit, [*self.condition_register, *self.quantum_adder_register], inplace=True)
        # self.__draw_master_circuit()
        for circ in adder_check_circuits:
            self.master_circuit.barrier()
            self.master_circuit.compose(circ, [*self.quantum_adder_register, *self.ancilla_register], inplace=True)
            # self.__draw_master_circuit()

        self.master_circuit.z(self.ancilla_register[-1])

        # reverse ops
        for circ in reversed(adder_check_circuits):
            self.master_circuit.compose(
                circ.reverse_ops(), [*self.quantum_adder_register, *self.ancilla_register], inplace=True)
            self.master_circuit.barrier()

        self.master_circuit.barrier()
        self.master_circuit.compose(
            adder_circuit.reverse_ops(), [*self.condition_register, *self.quantum_adder_register], inplace=True)
        self.master_circuit.barrier()
        self.master_circuit.compose(
            condition_check_circuit.reverse_ops(), [*self.board_moves_qbit_register, *self.condition_register], inplace=True)
        self.master_circuit.barrier()

        self.master_circuit.compose(diffusion, [*self.board_moves_qbit_register], inplace=True)
        self.__draw_master_circuit()


    def __schedule_job_locally(self, shots=10000, seed_simulator=None):
        """
        run circuit measurements locally on your PC with standard settings

        default simulator to use is 'qasm' that provides only counts and measurements, but any can be used
        :returns: job results
        """
        job = AerSimulator().run(self.master_circuit, shots=shots, seed_simulator=seed_simulator)
        self.current_job_shots = shots
        self.counts = job.result().get_counts(self.master_circuit)
        return self.counts

    def calculate_recommendations(
            self, valid_moves_list: MOVES_LIST_TYPEHINT, board: BOARD_TYPEHINT, current_player: str, enemy_player: str):
        """flag possible states, execute entire subcircuit creation, schedule a job and get results"""
        moves_count = len(valid_moves_list)
        self.q_allocate_registers(moves_count)

        # initialize states and flag conditions
        self.q_initialize()
        self.valid_moves_with_flags = self.assign_valid_board_moves_to_q_states(valid_moves_list)
        self.valid_moves_with_flags = self.condition_piece_shielded(
            board, self.valid_moves_with_flags, current_player, condition_num=1)
        self.valid_moves_with_flags = self.condition_moves_to_be_beaten(
            board, self.valid_moves_with_flags, enemy_player, condition_num=2)

        # this is for testing only and will be removed soon
        # self.valid_moves_with_flags =
        # {'000': [(5, 0, 4, 1), 0, 0, 0], '001': [(5, 2, 4, 3), 0, 0, 0], '010': [(5, 2, 4, 1), 0, 0, 0],
        #  '011': [(5, 4, 4, 5), 0, 0, 0], '100': [(5, 4, 4, 3), 0, 0, 0], '101': [(5, 6, 4, 7), 0, 0, 0],
        #  '110': [(5, 6, 4, 5), 0, 1, 0]}

        # prepare entire diffusion circuit based on flagged conditions
        self.q_prepare_iteration(1)
        self.master_circuit.measure(self.board_moves_qbit_register, self.results_register)
        self.__schedule_job_locally()

        print(
            {s: self.counts[s] for s in sorted(self.counts, key=lambda x: x)}
        )

    def parse_recommendations_bot_use(self):
        pass

    def parse_recommendations_human_readable(self):
        pass

    def __draw_master_circuit(self):
        if not self.verbose:
            return
        self.master_circuit.draw(output='mpl')
        plt.show()

    def __draw_circuit(self, circuit: QuantumCircuit):
        if not self.verbose:
            return
        circuit.draw(output='mpl')
        plt.show()


# Example Usage
if __name__ == '__main__':
    from game_logic import CheckersGame
    c_game = CheckersGame()
    # board = [[0 for _ in range(8)] for _ in range(8)]  # 8x8 board example
    print(c_game.valid_moves)
    print(c_game.human_readable_possible_moves())
    q_bot = QuantumBot(2)
    q_bot.calculate_recommendations(
        c_game.valid_moves, c_game.board, c_game.current_player, c_game.current_enemy_player
    )
