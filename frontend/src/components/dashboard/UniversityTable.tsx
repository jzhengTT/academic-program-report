import { useState, useEffect, type ChangeEvent, type ReactElement } from 'react';

import { useUniversities } from '../../hooks/useUniversities.ts';
import type { University } from '../../types/university.ts';
import './UniversityTable.css';

type SortField = 'university_name' | 'researchers_count' | 'students_count' | 'created_at';

interface SortableHeaderProps {
  field: SortField;
  label: string;
  currentSort: SortField;
  onSort: (field: SortField) => void;
}

function SortableHeader({ field, label, currentSort, onSort }: SortableHeaderProps): ReactElement {
  const isSorted = currentSort === field;
  return (
    <th className={isSorted ? 'sorted' : ''} onClick={() => onSort(field)}>
      {label}
      {isSorted && <span className="sort-icon">↓</span>}
    </th>
  );
}

function HardwareTags({ types }: { types: string[] }): ReactElement {
  if (types.length === 0) {
    return <span className="no-hardware">-</span>;
  }
  return (
    <>
      {types.map((hw, idx) => (
        <span key={idx} className="hardware-tag">{hw}</span>
      ))}
    </>
  );
}

function UniversityRow({ uni }: { uni: University }): ReactElement {
  const dateAdded = new Date(uni.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  return (
    <tr>
      <td className="university-name">{uni.university_name}</td>
      <td className="number">{uni.researchers_count.toLocaleString()}</td>
      <td className="number">{uni.students_count.toLocaleString()}</td>
      <td>{uni.point_of_contact || '-'}</td>
      <td>{dateAdded}</td>
      <td>
        <div className="hardware-tags">
          <HardwareTags types={uni.hardware_types} />
        </div>
      </td>
    </tr>
  );
}

export function UniversityTable(): ReactElement {
  const [sortBy, setSortBy] = useState<SortField>('researchers_count');
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filterTenstorrent, setFilterTenstorrent] = useState(true);
  const { data, isLoading, error } = useUniversities(debouncedSearch || undefined, sortBy, filterTenstorrent);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  function handleSearchChange(e: ChangeEvent<HTMLInputElement>): void {
    setSearchInput(e.target.value);
  }

  const hasUniversities = data && data.universities.length > 0;

  return (
    <div className="university-table-container">
      <div className="table-header">
        <h3>All Universities ({data?.total ?? 0})</h3>
        <div className="filters">
          <label className="filter-toggle">
            <input
              type="checkbox"
              checked={filterTenstorrent}
              onChange={(e) => setFilterTenstorrent(e.target.checked)}
            />
            <span>Has Hardware</span>
          </label>
          <input
            type="text"
            placeholder="Search universities..."
            value={searchInput}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="loading">Loading universities...</div>
      ) : error ? (
        <div className="error">Failed to load universities</div>
      ) : !hasUniversities ? (
        <div className="no-data">
          No universities found. Sync data from Asana to populate this table.
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="university-table">
            <thead>
              <tr>
                <SortableHeader field="university_name" label="University Name" currentSort={sortBy} onSort={setSortBy} />
                <SortableHeader field="researchers_count" label="Researchers" currentSort={sortBy} onSort={setSortBy} />
                <SortableHeader field="students_count" label="Students" currentSort={sortBy} onSort={setSortBy} />
                <th>Point of Contact</th>
                <SortableHeader field="created_at" label="Date Added" currentSort={sortBy} onSort={setSortBy} />
                <th>Hardware</th>
              </tr>
            </thead>
            <tbody>
              {data.universities.map((uni) => (
                <UniversityRow key={uni.asana_task_gid} uni={uni} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
