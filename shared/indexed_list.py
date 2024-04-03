from typing import TypeVar, Generic, Mapping, Callable, List, Iterator
from collections.abc import Iterable

T = TypeVar('T')

class IndexedList(Generic[T], Iterable[T]):
    """A generic, indexed list that maintains a list of entries and a lookup mapping for fast access.

    Attributes:
        lookup (Mapping[str, T]): A dictionary for fast lookup of entries by a string index.
        entries (List[T]): A list of entries maintaining the order of insertion.
        resolve_index (Callable[[T], str]): A function to resolve the string index for each entry.
    """

    def __init__(self, resolve_index: Callable[[T], str], entries: List[T] = []):
        """Initialize the IndexedList with a function to resolve indexes and an optional list of initial objects.

        Parameters:
            resolve_index (Callable[[T], str]): Function to determine the index for each entry.
            entries (List[T], optional): Initial list of entries to add. Defaults to an empty list.
        """

        self.lookup: Mapping[str, T] = {}
        self.entries: List[T] = []
        self.resolve_index = resolve_index

        self.add_entries(entries)

    def add_entry(self, entry: T) -> None:
        """Add a single entry to the indexed list.

        Parameters:
            entry (T): The entry to add.

        Raises:
            ValueError: If an entry with the same index already exists in the list.

        Returns:
            None
        """
        index = self.resolve_index(entry)

        if index in self.lookup:
            raise ValueError(f"Addition failed: Entry with index '{index}' already exists.")

        self.lookup[index] = entry
        self.entries.append(entry)

    def add_entries(self, entries: List[T]) -> None:
        """Add multiple entries to the indexed list.

        Parameters:
            entries (List[T]): The list of entries to add.

        Raises:
            ValueError: If an element of `entries` has an index already in the list.

        Returns:
            None
        """
        for entry in entries:
            self.add_entry(entry)

    def upsert_entry(self, entry: T) -> None:
        """Update an existing entry or insert a new one based on the resolved index.

        Parameters:
            entry (T): The entry to update or insert.

        Returns:
            None
        """
        index = self.resolve_index(entry)

        if index in self.lookup:
            self.delete_entry(entry)

        self.add_entry(entry)

    def upsert_entries(self, entries: List[T]) -> None:
        """Update existing entries or insert new ones in bulk.

        Parameters:
            entries (List[T]): The list of entries to update or insert.

        Returns:
            None
        """
        for entry in entries:
            self.upsert_entry(entry)

    def delete_entry(self, entry: T) -> None:
        """Delete an entry based on its resolved index.

        Parameters:
            entry (T): The entry to delete.

        Raises:
            KeyError: If no entry exists with the specified index.

        Returns:
            None
        """
        del self[self.resolve_index(entry)]

    def delete_entries(self, entries: List[T]) -> None:
        """Delete multiple entries based on their resolved indexes.

        Parameters:
            entries (List[T]): The list of entries to delete.

        Raises:
            KeyError: If an element of `entries` has an index not in the list.

        Returns:
            None
        """
        for entry in entries:
            self.delete_entry(entry)

    def __delitem__(self, key: str) -> None:
        """Delete an entry by its index.

        Parameters:
            key (str): The index of the entry to delete.

        Raises:
            KeyError: If no entry exists with the specified index.
        """
        if key in self.lookup:
            self.entries = [entry for entry in self.entries if self.resolve_index(entry) != key]
            del self.lookup[key]
        else:
            raise KeyError(f"Deletion failed: entry with index '{key}' not found.")

    def __getitem__(self, key: str) -> T:
        """Retrieve an entry by its index.

        Parameters:
            key (str): The index of the entry to retrieve.

        Returns:
            T: The entry associated with the specified index.
        """

        if key in self.lookup:
            return self.lookup[key]
        else:
            raise KeyError(f"Lookup failed: entry with index '{key}' not found.")

    def __iter__(self) -> Iterator[T]:
        """Create an iterator for the list of entries.

        Returns:
            Iterator[T]: An iterator over the entries.
        """
        return iter(self.entries)

    def __str__(self) -> str:
        """Returns a string representation of the list.

        Returns:
            str: The representation of the list.
        """
        return self.lookup.__str__()

    def __len__(self) -> int:
        """Returns the number of items in the list.

        Returns:
            int: The number of items in the list.
        """
        return len(self.entries)