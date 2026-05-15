from .raw import RawHub, RawConnection, RawMap


class ParserError(Exception):
    ...


class Parser:
    def __init__(self) -> None:
        self.first_token_seen = False

    @staticmethod
    def error_l(line_number: int, error: str) -> str:
        return f"at line {line_number} {error}"

    def parse_file(self, path: str) -> RawMap:
        self._raw_map = RawMap(nb_drones=0, hubs=[], connections=[])
        with open(path, "r") as file:
            for line_number, line in enumerate(file, 1):
                self._parse_line(line.strip(), line_number)
        return self._raw_map

    def _parse_line(
            self, line: str, line_number: int) -> None:
        if not line or line.startswith("#"):
            return
        tok = line.strip().split(" ")
        if not self.first_token_seen:
            if tok[0] != "nb_drones:":
                raise ParserError(
                    f"first line must be nb_drones at line {line_number}")
            self.first_token_seen = True
        if tok[0] == "nb_drones:":
            if len(tok) < 2:
                raise ParserError(
                    Parser.error_l(line_number, tok[0])
                    + " needs another argument")
            else:
                self._raw_map.nb_drones = (int(tok[1]))
        elif tok[0] == "hub:" or tok[0] == "start_hub:" \
                or tok[0] == "end_hub:":
            self._raw_map.hubs.append(self._parse_hub(
                tok, line_number, 4))
        elif tok[0] == "connection:":
            self._raw_map.connections.append(
                self._parse_connection(
                    tok, line_number, 2))
        else:
            raise ParserError(
                f"Line Number: {line_number} is not interpreted")

    def _parse_hub(
            self, toks: list[str],
            line_number: int, len_min: int) -> RawHub:
        if len(toks) < len_min:
            raise ParserError(
                "at line:"
                f"{line_number} you wrote "
                f"{len(toks)} args, needed at least: {len_min}")
        try:
            int(toks[2])
            int(toks[3])
        except ValueError as e:
            raise ParserError(f"error {e} at line {line_number}")
        return RawHub(
            kind=toks[0].strip(":"),
            name=toks[1],
            x=int(toks[2]),
            y=int(toks[3]),
            metadata=(self._parse_metadata(
                " ".join(toks[len_min:]), line_number)
                if len(toks) >= len_min + 1 else None)
        )

    def _parse_connection(
            self, toks: list[str],
            line_number: int, len_min: int) -> RawConnection:
        if len(toks) < len_min:
            raise ParserError("no parameter found for ",
                              toks, "at line: ", line_number)
        if "-" not in toks[1]:
            raise ParserError(
                f"error at line {line_number}, ({toks[1]}) is not correct")
        edges = toks[1].split("-")
        if len(edges) != 2:
            raise ParserError(
                f"error at line {line_number}, ({edges}) is not correct")
        a, b = edges
        return RawConnection(
                a=a,
                b=b,
                metadata=(self._parse_metadata(
                    " ".join(toks[len_min:]), line_number)
                    if len(toks) >= len_min + 1 else None)
            )

    def _parse_metadata(self, raw: str,
                        line_number: int) -> dict[str, str] | None:
        res = {}
        if raw.startswith("[") and raw.endswith("]"):
            tokens = raw.strip("[]").split()
            tokens2 = (tok.split("=") for tok in tokens)
            for tok in tokens2:
                if "[" in tok or "]" in tok:
                    raise ParserError(
                        f"at line  {line_number} {tok} is not a correct token")
                res[tok[0]] = tok[1]
            if len(tok) > 2:
                raise ParserError(
                    f"bad formatting of {tok} at line {line_number}")
            return res
        else:
            raise ParserError(
                "bad metadata formating of ", raw, ", at line ", line_number
            )
