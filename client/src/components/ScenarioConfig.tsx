import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useAppState } from "@/hooks/useAppState";
import { createScenario } from "@/lib/scenario";
import { useState } from "react";

interface Props {
  onScenarioCreated: () => void;
  onCancel: () => void;
}

export function ScenarioConfig({ onScenarioCreated, onCancel }: Props) {
  const { setScenarioConfig } = useAppState();
  const [username, setUsername] = useState("");
  const [scenario, setScenario] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [otherInstructions, setOtherInstructions] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const scenarioResponse = await createScenario({
        level: difficulty,
        topic: scenario,
        other_instructions: otherInstructions,
      });

      // Store scenario configuration in app state
      setScenarioConfig({
        language: "",
        scenario_title: scenario,
        scenario: scenarioResponse.scenario,
        level: difficulty,
        metrics: scenarioResponse.metrics,
      });

      onScenarioCreated();
    } catch (error) {
      console.error('Error creating scenario:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Role Play Bot Configuration</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="username">USERNAME</Label>
          <Input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="scenario">SCENARIO</Label>
          <Select value={scenario} onValueChange={setScenario}>
            <SelectTrigger>
              <SelectValue placeholder="Select scenario" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="product_offering">Product Offering</SelectItem>
              <SelectItem value="customer_complaint">Customer Complaint</SelectItem>
              <SelectItem value="claim_processing">Claim Processing</SelectItem>
              <SelectItem value="policy_renewal">Policy Renewal</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="difficulty">DIFFICULTY LEVEL</Label>
          <Select value={difficulty} onValueChange={setDifficulty}>
            <SelectTrigger>
              <SelectValue placeholder="Select difficulty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="new_hire">New Hire</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="expert">Expert</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="other-instructions">OTHER INSTRUCTIONS</Label>
          <Textarea
            id="other-instructions"
            value={otherInstructions}
            onChange={(e) => setOtherInstructions(e.target.value)}
            placeholder="Enter any additional instructions"
            className="h-24"
          />
        </div>

        <div className="flex justify-end space-x-4">
          <Button variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Generating...
              </>
            ) : (
              'Generate Scenario'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
} 