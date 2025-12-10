"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Settings2, Loader2, Search } from "lucide-react" // Ensure lucide-react is available (shadcn installs it)
import { ResearchRequest } from "@/lib/api"

interface ResearchFormProps {
    onSubmit: (data: ResearchRequest) => void;
    isLoading: boolean;
}

export default function ResearchForm({ onSubmit, isLoading }: ResearchFormProps) {
    const [query, setQuery] = useState("")
    const [showOptions, setShowOptions] = useState(false)
    const [count, setCount] = useState(5)
    const [lang, setLang] = useState("Korean")

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim()) return
        onSubmit({ query, count, lang, mode: "stream", format: "markdown" })
    }

    return (
        <Card className="w-full max-w-2xl mx-auto shadow-lg border-neutral-200 dark:border-neutral-800 bg-white/50 dark:bg-neutral-900/50 backdrop-blur-sm">
            <CardHeader>
                <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                    Deep Research Agent
                </CardTitle>
                <CardDescription>
                    Enter a topic to generate a comprehensive research report.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex gap-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="e.g. 'Future of Quantum Computing'"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="pl-9 h-12 text-lg"
                                disabled={isLoading}
                            />
                        </div>
                        <Button type="button" variant="outline" size="icon" className="h-12 w-12 shrink-0" onClick={() => setShowOptions(!showOptions)}>
                            <Settings2 className="h-5 w-5" />
                        </Button>
                    </div>

                    {showOptions && (
                        <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-neutral-100 dark:bg-neutral-800/50 animate-in fade-in slide-in-from-top-2">
                            <div className="space-y-2">
                                <Label>Source Count</Label>
                                <Input
                                    type="number"
                                    min={1}
                                    max={20}
                                    value={count}
                                    onChange={(e) => setCount(Number(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Language</Label>
                                <Input
                                    value={lang}
                                    onChange={(e) => setLang(e.target.value)}
                                />
                            </div>
                        </div>
                    )}

                    <Button type="submit" className="w-full h-12 text-lg font-medium bg-blue-600 hover:bg-blue-700 transition-all" disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                Researching...
                            </>
                        ) : (
                            "Start Research"
                        )}
                    </Button>
                </form>
            </CardContent>
        </Card>
    )
}
