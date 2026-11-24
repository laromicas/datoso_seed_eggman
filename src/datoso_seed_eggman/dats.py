"""DAT files for Eggman."""
import re
from pathlib import Path

from datoso.repositories.dat_file import DirMultiDatFile, XMLDatFile


def header_field(dat: Path, field: str) -> str | None:
    """Read a header field (e.g. date, version) from the start of an XML DAT, without parsing all of it."""
    with dat.open(encoding='utf-8', errors='ignore') as file:
        found = re.search(rf'<{field}>([^<]*)</{field}>', file.read(65536))
    return found.group(1).strip() or None if found else None


class TeknoparrotDat(DirMultiDatFile):
    """Teknoparrot DAT file."""

    seed: str = 'eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.system = self.name
        self.company = getattr(self, 'company', None)
        self.prefix = 'Arcade'
        self.suffix = getattr(self, 'suffix', None)
        find_system = self.overrides()
        self.extra_configs(find_system)
        self.full_name = f'{self.header["description"]} - {self.system}' if self.header.get('description', None) else None

        return [None, self.company, self.system, self.suffix, self.get_date()]

    def dat_files(self) -> list[Path]:
        """List the DATs in this folder (recursively)."""
        return sorted(path for path in Path(self.file).rglob('*')
                      if path.is_file() and path.suffix.lower() in ('.dat', '.xml'))

    def get_date(self) -> str | None:
        """Newest header <date> (or file name date) of the DATs, so unchanged folders are skipped."""
        if self.date is None:
            dates = [header_field(dat, 'date') or next(iter(re.findall(r'\d{4}-\d{2}-\d{2}', dat.name)), None)
                     for dat in self.dat_files()]
            self.date = max((date for date in dates if date), default=None)
        return self.date

    def get_version(self) -> str | None:
        """Header <version>, else the DATs' total size: same-date re-releases (Rev.1, fixed) still differ."""
        if self.version is None:
            dats = self.dat_files()
            versions = [version for dat in dats if (version := header_field(dat, 'version'))]
            self.version = ' + '.join(versions) if versions else \
                (str(sum(dat.stat().st_size for dat in dats)) if dats else None)
        return self.version


class EggmanDat(XMLDatFile):
    """Eggman DAT file."""

    seed: str = 'Eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.prefix = ''
        self.company = ''
        self.system = ''
        self.suffix = ''
        self.date = ''

        return [self.prefix, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        return self.date

class SegaALLDotNetDat(XMLDatFile):
    """SegaALLDotNet DAT file."""

    seed: str = 'eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.system = self.name
        self.company = getattr(self, 'company', None)
        self.prefix = 'Arcade'
        self.suffix = getattr(self, 'suffix', None)
        find_system = self.overrides()
        self.extra_configs(find_system)
        self.full_name = f'{self.header["description"]} - {self.system}' if self.header.get('description', None) else None

        return [None, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        return self.date

class TouhouDat(DirMultiDatFile):
    """Touhou DAT file."""
