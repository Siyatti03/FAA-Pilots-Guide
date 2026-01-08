import React, { useEffect, useState } from "react";
import SearchBoxLoader from "./CategoriesLoader";
import { ItemData } from "../../types"

// This is a VERY simple search function, seperated for maintainability such that the algo can be replaced
function searchMatches(item: ItemData, query: string): boolean {
  if (!query) return true;
  const q = query.toLowerCase();

  //If NEEDED this is where you would sanitize, with this search function we don't need it

  return (
    item.name.toLowerCase().includes(q) ||
    item.description.toLowerCase().includes(q) ||
    item.med_cert_importance.toLowerCase().includes(q) ||
    item.category.toLowerCase().includes(q)
  );
}

const SearchableDataViewer: React.FC = () => {
  const [query, setQuery] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [activeCategories, setActiveCategories] = useState<string[]>([]);

  useEffect(() => {
    fetch("/data/index.json")
      .then(res => res.json())
      .then(data => {
        const categories = data.files.map((f: any) => f.category);
        setCategories(categories);
        setActiveCategories(categories); // The default behavior is that all categories are visible
      });
  }, []);

  function toggleCategory(category: string) {
    setActiveCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  }

  return (
    <div className = "card-outer" role= "region" aria-label="Term Search Component">
      {/* Search bar */}
      <input
        type="text"
        className= "search-bar"
        placeholder="Search terms..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        role = "searchbox"
        aria-label = "Search Term Input"
      />

      {/* Tags for filtering */}
      <div className= "filter-bar" role  = "reigon">
        {categories.map((category) => (
          <button
            key={category}
            role = "button"
            className={activeCategories.includes(category) ? "active" : ""}
            onClick={(e) => {
              toggleCategory(category);
              e.currentTarget.blur(); //Remove focus after click
            }}
            aria-pressed = {activeCategories.includes(category)}
            aria-label = {`Filter by category ${category}`}>
            {category}
          </button>
        ))}
      </div>

      {/* Pass search logic to DataLoader */}
      <SearchBoxLoader
        filterFunction={(item: ItemData) =>
          searchMatches(item, query)
        }
        searchActive={!!query}
        activeCategories={activeCategories}/>
    </div>
  );
};

export default SearchableDataViewer;
