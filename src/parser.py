# config_parser.py

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    map: list[list[int]]

    start: tuple[int, int] = (0, 0)
    sight_range: int = 0

    charge_per_movement: float = 0.0
    charge_per_vacuum: float = 0.0
    power_station_loc: tuple[int, int] | None = None

    cell_dirt_prob: float = 0.0
    random_seed: int | None = None
    max_steps: int | None = None


def _parse_position(value: str) -> tuple[int, int]:
    """Converte uma string 'linha,coluna' para uma tupla."""
    try:
        row, col = value.split(",")
        return int(row), int(col)
    except ValueError as exc:
        raise ValueError(
            f"Posição inválida: {value!r}. "
            "Use o formato linha,coluna."
        ) from exc


def _validate_map(map_: list[list[int]]) -> None:
    if not map_:
        raise ValueError("O arquivo não contém um mapa.")

    width = len(map_[0])

    if width == 0:
        raise ValueError("O mapa não pode possuir linhas vazias.")

    for i, row in enumerate(map_):
        if len(row) != width:
            raise ValueError(
                f"Linha {i} possui {len(row)} células; "
                f"esperadas {width}."
            )

        for cell in row:
            if cell not in (0, 1, 9):
                raise ValueError(
                    f"Valor inválido no mapa: {cell}. "
                    "Valores permitidos: 0, 1 e 9."
                )


def _validate_position(
    position: tuple[int, int],
    map_: list[list[int]],
    name: str,
) -> None:
    row, col = position
    height = len(map_)
    width = len(map_[0])

    if not (0 <= row < height and 0 <= col < width):
        raise ValueError(
            f"{name}={row},{col} está fora dos limites do mapa."
        )

    if map_[row][col] == 9:
        raise ValueError(
            f"{name}={row},{col} está localizado sobre um obstáculo."
        )


def load_config(filename: str | Path) -> Config:
    """Lê um arquivo de configuração do mundo do aspirador.

    Linhas contendo apenas 0, 1 e 9 representam o mapa. As demais configurações
    possuem a forma:
    CHAVE:valor

    Parameters
    ----------
    filename: str, Path
        Caminho para o arquivo com as configurações

    Returns
    -------
    config: Config
        A estrutura de configuração com informações do mapa, localização do
        agente, carredagor, consumo de carga, etc.
    """

    filename = Path(filename)

    map_: list[list[int]] = []
    options: dict[str, str] = {}

    with filename.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()

            # Ignora linhas vazias e comentários.
            if not line or line.startswith("#"):
                continue

            # Parâmetro de configuração
            if ":" in line:
                key, value = line.split(":", maxsplit=1)

                key = key.strip().upper()
                value = value.strip()

                if not value:
                    raise ValueError(
                        f"Linha {line_number}: "
                        f"valor ausente para {key}."
                    )

                options[key] = value

            # Linha do mapa
            else:
                try:
                    row = [int(c) for c in line]
                except ValueError as exc:
                    raise ValueError(
                        f"Linha {line_number}: "
                        f"linha de mapa inválida: {line!r}."
                    ) from exc

                map_.append(row)

    _validate_map(map_)

    known_options = {
        "START",
        "SIGHT-RANGE",
        "CHARGE-PER-MOVEMENT",
        "CHARGE-PER-VACUUM",
        "POWER-STATION-LOC",
        "CELL-DIRT-PROB",
        "RANDOM-SEED",
        "MAX-STEPS",
    }

    unknown_options = set(options) - known_options

    if unknown_options:
        raise ValueError(
            "Parâmetro(s) desconhecido(s): "
            + ", ".join(sorted(unknown_options))
        )

    start = _parse_position(
        options.get("START", "0,0")
    )

    sight_range = int(
        options.get("SIGHT-RANGE", "0")
    )

    charge_per_movement = float(
        options.get("CHARGE-PER-MOVEMENT", "0")
    )

    charge_per_vacuum = float(
        options.get("CHARGE-PER-VACUUM", "0")
    )

    if "POWER-STATION-LOC" in options:
        power_station_loc = _parse_position(
            options["POWER-STATION-LOC"]
        )
    else:
        power_station_loc = start

    cell_dirt_prob = float(
        options.get("CELL-DIRT-PROB", "0")
    )

    random_seed = (
        int(options["RANDOM-SEED"])
        if "RANDOM-SEED" in options
        else 42
    )

    max_steps = (
        int(options["MAX-STEPS"])
        if "MAX-STEPS" in options
        else None
    )

    _validate_position(start, map_, "START")
    _validate_position(
        power_station_loc,
        map_,
        "POWER-STATION-LOC",
    )

    if sight_range < 0:
        raise ValueError(
            "SIGHT-RANGE não pode ser negativo."
        )

    if charge_per_movement < 0:
        raise ValueError(
            "CHARGE-PER-MOVEMENT não pode ser negativo."
        )

    if charge_per_vacuum < 0:
        raise ValueError(
            "CHARGE-PER-VACUUM não pode ser negativo."
        )

    if not (0.0 <= cell_dirt_prob <= 1.0):
        raise ValueError(
            "CELL-DIRT-PROB deve estar entre 0 e 1."
        )

    if max_steps is not None and max_steps <= 0:
        raise ValueError(
            "MAX-STEPS deve ser maior que zero."
        )

    return Config(
        map=map_,
        start=start,
        sight_range=sight_range,
        charge_per_movement=charge_per_movement,
        charge_per_vacuum=charge_per_vacuum,
        power_station_loc=power_station_loc,
        cell_dirt_prob=cell_dirt_prob,
        random_seed=random_seed,
        max_steps=max_steps,
    )


if __name__ == '__main__':
    config = load_config("input2.txt")
    print(config.map)
    print(config.start)
    print(config.sight_range)
