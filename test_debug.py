"""Debug script to test test generation."""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.test_generation.application.services import EquivalencePartitionService

async def main():
    service = EquivalencePartitionService()
    
    analysis_file = "output/swagger/gestión_de_prioridades_api_20251125_194956.json"
    
    try:
        print(f"Loading analysis from: {analysis_file}")
        results = await service.generate_test_cases_from_json(analysis_file)
        
        print(f"\nResults: {len(results)} endpoints processed")
        for result in results:
            print(f"  - {result.http_method} {result.endpoint}: {len(result.test_cases)} test cases")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
