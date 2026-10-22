from dataclasses import dataclass


@dataclass
class Colis:
    """Colis avec ID unique, poids, valeur, priorité et destination."""

    id: int
    poids: int  # kg
    valeur: int
    priorite: int  # de 1 (la moins urgente) à x (la plus urgente)
    destination: str  # ville de destination du colis

    def __str__(self):
        return (
            f"{self.id} | {self.poids} kg | {self.valeur} | "
            f"{self.priorite:>4} | {self.destination}"
        )
