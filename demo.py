# this file will contain script, that when run, shows off the project contents

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.result.result import Result
from qiskit_aer import AerSimulator
from matplotlib import pyplot as plt


q_reg = QuantumRegister(2)
c_reg = ClassicalRegister(2)

q_circ = QuantumCircuit(q_reg, c_reg)
q_circ.x(0)
q_circ.measure(q_reg, c_reg)

q_circ.draw(output='mpl')
plt.show()

job = AerSimulator().run(q_circ)
result: Result = job.result()
print(result.get_counts(q_circ))


