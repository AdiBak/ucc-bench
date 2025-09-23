from qiskit_aer.noise import NoiseModel
from qiskit_aer import AerSimulator
from ucc_bench import registry

target_device = registry.register.get_target_device("ibm_fake_washington")
noise_model = NoiseModel.from_backend(target_device)
simulator = AerSimulator(method="density_matrix", noise_model=noise_model)

# Confirm it is a density matrix simulator
print(simulator.name)
# print(simulator.properties)
