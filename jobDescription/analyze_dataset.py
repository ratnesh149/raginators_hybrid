#!/usr/bin/env python3
import csv
import json

def analyze_dataset():
    try:
        with open('dataset.csv', 'r', encoding='utf-8') as file:
            # Read the CSV file
            csv_reader = csv.DictReader(file)
            candidates = list(csv_reader)
            
            print(f"Dataset Analysis:")
            print(f"Total candidates: {len(candidates)}")
            print(f"Columns: {list(candidates[0].keys()) if candidates else 'No data'}")
            
            if candidates:
                print(f"\nFirst candidate sample:")
                first_candidate = candidates[0]
                for key, value in first_candidate.items():
                    print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                
                # Count decisions
                decisions = {}
                roles = {}
                for candidate in candidates:
                    decision = candidate.get('decision', 'unknown').lower()
                    role = candidate.get('Role', 'Unknown')
                    
                    decisions[decision] = decisions.get(decision, 0) + 1
                    roles[role] = roles.get(role, 0) + 1
                
                print(f"\nDecision distribution:")
                for decision, count in decisions.items():
                    print(f"  {decision}: {count}")
                
                print(f"\nTop 5 roles:")
                sorted_roles = sorted(roles.items(), key=lambda x: x[1], reverse=True)[:5]
                for role, count in sorted_roles:
                    print(f"  {role}: {count}")
                
                # Create a sample JSON for the web app
                sample_data = candidates[:3]  # First 3 candidates
                with open('sample_candidates.json', 'w', encoding='utf-8') as json_file:
                    json.dump(sample_data, json_file, indent=2, ensure_ascii=False)
                print(f"\nSample data saved to sample_candidates.json")
                
    except FileNotFoundError:
        print("dataset.csv not found in current directory")
    except Exception as e:
        print(f"Error analyzing dataset: {e}")

if __name__ == "__main__":
    analyze_dataset()
