"""Gere commits staged com o Codex CLI."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from git import InvalidGitRepositoryError, Repo

INSTRUCTIONS_PATH = Path(
    ".github/copilot-commit-message-instructions.md",
)
OUTPUT_DIRECTORY = Path("commit-message")


def staged_diff(repo: Repo) -> str:
    """Retorne o diff staged do repositório.

    Args:
        repo: Repositório Git usado na leitura do índice.

    Returns:
        Diff das alterações adicionadas ao índice.

    Raises:
        ValueError: Quando não existem alterações staged.

    """
    diff = repo.git.diff("--cached", "--no-ext-diff", "--binary")

    if not diff.strip():
        diff = repo.git.diff("--binary")

    if not diff.strip():
        msg = "Nenhuma alteração staged encontrada."
        raise ValueError(msg)
    return diff


def build_prompt(instructions: str, diff: str) -> str:
    """Monte o prompt restrito à geração da mensagem de commit.

    Args:
        instructions: Regras obrigatórias para a mensagem.
        diff: Alterações staged do repositório.

    Returns:
        Prompt completo enviado ao Codex.

    """
    return f"""Gere somente a mensagem de commit final em Markdown.
Não use cercas de código. Não explique a resposta.
Siga rigorosamente estas instruções:

{instructions}

Alterações staged:

{diff}
"""


def generate_message(
    root: Path,
    timestamp: datetime | None = None,
) -> Path:
    """Gere e salve uma mensagem para as alterações staged.

    Args:
        root: Raiz do repositório Git.
        timestamp: Horário opcional usado no nome do arquivo.

    Returns:
        Caminho da mensagem gerada.

    Raises:
        FileNotFoundError: Quando faltam instruções ou o Codex CLI.
        InvalidGitRepositoryError: Quando ``root`` não é repositório.

    """
    repo = Repo(root, search_parent_directories=True)
    working_tree = repo.working_tree_dir
    if working_tree is None:
        raise InvalidGitRepositoryError(root)
    repository_root = Path(working_tree)
    instructions_path = repository_root / INSTRUCTIONS_PATH
    instructions = instructions_path.read_text(encoding="utf-8")
    diff = staged_diff(repo)

    codex = shutil.which("codex")
    if codex is None:
        msg = "Codex CLI não encontrado no PATH."
        raise FileNotFoundError(msg)

    output_directory = repository_root / OUTPUT_DIRECTORY
    output_directory.mkdir(exist_ok=True)
    generated_at = timestamp or datetime.now().astimezone()
    output_path = output_directory / generated_at.strftime(
        "%Y%m%d-%H%M%S.md",
    )

    subprocess.run(
        [
            codex,
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--cd",
            str(repository_root),
            "--output-last-message",
            str(output_path),
            "-",
        ],
        input=build_prompt(instructions, diff),
        text=True,
        encoding="utf-8",
        check=True,
    )
    return output_path


def main() -> None:
    """Execute o gerador pela linha de comando."""
    parser = argparse.ArgumentParser(
        description=(
            "Gera mensagem de commit para as alterações staged."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        output_path = generate_message(args.root)
    except (
        FileNotFoundError,
        InvalidGitRepositoryError,
        ValueError,
    ) as error:
        parser.error(str(error))

    subprocess.run(["code", str(output_path)], shell=True, check=False)


if __name__ == "__main__":
    main()
