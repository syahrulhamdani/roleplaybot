import { useAppState } from "@/hooks/useAppState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpenIcon, TargetIcon, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

interface Props {
  className?: string;
}

function toTitleCase(str: string) {
  return str
    .replace(/_/g, ' ')
    .replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
}

export default function ScenarioDisplay({ className }: Props) {
  const { scenarioConfig } = useAppState();
  const [open, setOpen] = useState(true);

  if (!scenarioConfig) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3 flex flex-row items-center justify-between cursor-pointer select-none" onClick={() => setOpen((v) => !v)}>
        <div className="flex items-center gap-2">
          <BookOpenIcon className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg">Scenario</CardTitle>
          <Badge variant="secondary" className="capitalize">
            {scenarioConfig.level.replace('_', ' ')}
          </Badge>
        </div>
        <button
          type="button"
          aria-label={open ? "Collapse scenario" : "Expand scenario"}
          className="ml-2 p-1 rounded hover:bg-muted/60 focus:outline-none"
          tabIndex={0}
          onClick={e => { e.stopPropagation(); setOpen((v) => !v); }}
        >
          {open ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
        </button>
      </CardHeader>
      <CardContent
        className={`pt-0 transition-all duration-300 ease-in-out overflow-hidden ${open ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0 pointer-events-none'}`}
        aria-hidden={!open}
      >
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-sm text-muted-foreground mb-2">
              {toTitleCase(scenarioConfig.scenario_title)}
            </h4>
            <div className="text-sm whitespace-pre-wrap leading-relaxed text-muted-foreground">
              {scenarioConfig.scenario}
            </div>
          </div>
          {scenarioConfig.metrics && scenarioConfig.metrics.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <TargetIcon className="h-4 w-4 text-primary" />
                <h5 className="font-semibold text-sm">Assessment Metrics</h5>
              </div>
              <div className="space-y-2">
                {scenarioConfig.metrics.map((metric, index) => (
                  <div key={index} className="p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-start justify-between mb-1">
                      <h6 className="font-medium text-sm">{metric.metric}</h6>
                      {/* <Badge variant="outline" className="text-xs">
                        {metric.min_score}-{metric.max_score}
                      </Badge> */}
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {metric.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 