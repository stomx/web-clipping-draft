"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Terminal, CheckCircle2, Circle } from "lucide-react"

interface LiveStatusProps {
    logs: string[];
    status: "idle" | "searching" | "extracting" | "summarizing" | "reporting" | "completed" | "failed";
}

export default function LiveStatus({ logs, status }: LiveStatusProps) {
    return (
        <Card className="w-full bg-black border-neutral-800 shadow-xl overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-neutral-800 bg-neutral-900/50 flex flex-row items-center gap-2">
                <Terminal className="h-4 w-4 text-green-500" />
                <CardTitle className="text-sm font-mono text-neutral-400">Live Agent Console</CardTitle>
                <span className="ml-auto flex items-center gap-2 text-xs font-mono">
                    {status === "idle" ? (
                        <span className="text-neutral-500">IDLE</span>
                    ) : (
                        <span className="text-green-500 animate-pulse uppercase">{status}</span>
                    )}
                </span>
            </CardHeader>
            <CardContent className="p-0">
                <ScrollArea className="h-[300px] w-full p-4 font-mono text-sm text-green-400/80">
                    <div className="flex flex-col gap-1.5">
                        {logs.length === 0 && <span className="text-neutral-600 italic">// Ready for input...</span>}
                        {logs.map((log, index) => (
                            <div key={index} className="flex gap-2 items-start break-words">
                                <span className="text-neutral-600 shrink-0 select-none">$</span>
                                <span className="opacity-90">{log}</span>
                            </div>
                        ))}
                        {/* Auto-scroll anchor could be here */}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    )
}
