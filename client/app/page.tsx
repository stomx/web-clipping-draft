"use client"

import { useState, useEffect } from "react"
import ResearchForm from "@/components/ResearchForm"
import LiveStatus from "@/components/LiveStatus"
import ReportViewer from "@/components/ReportViewer"
import { ResearchRequest, streamResearch } from "@/lib/api"
import { Separator } from "@/components/ui/separator"

export default function Home() {
  const [logs, setLogs] = useState<string[]>([])
  const [status, setStatus] = useState<"idle" | "searching" | "extracting" | "summarizing" | "reporting" | "completed" | "failed">("idle")
  const [report, setReport] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const buildPartialReport = (query: string, summaries: string[]) => {
    let report = `# Research Report: ${query}\n\n`

    // Process summaries directly
    const items: any[] = []
    summaries.forEach(s => {
      try {
        const item = typeof s === 'string' ? JSON.parse(s) : s
        items.push(item)
      } catch (e) {
        // Skip invalid summaries
      }
    })

    // Build markdown
    for (const item of items) {
      report += `### ${item.title}\n\n`
      if (Array.isArray(item.summary)) {
        item.summary.forEach((point: string) => {
          report += `- ${point}\n`
        })
      }
      const dateStr = item.date ? ` (${item.date})` : ""
      report += `\n**출처**: [${item.source}](${item.source})${dateStr}\n\n`
      if (item.thumbnail) {
        report += `![thumbnail](${item.thumbnail})\n\n`
      }
      report += `---\n\n`
    }

    return report
  }

  const handleResearch = async (req: ResearchRequest) => {
    console.log("Starting research for:", req.query);
    setIsLoading(true)
    setStatus("searching")
    setLogs([])
    setReport("")

    // Accumulator for streaming summaries
    const allSummaries: string[] = []

    try {
      setLogs(prev => [...prev, `Initializing research for: "${req.query}"`])

      const stream = streamResearch(req)
      let allSummaries: string[] = []

      for await (const event of stream) {
        console.log("Received event:", JSON.stringify(event, null, 2));

        // 1. Handle Granular Streaming (One Summary at a time)
        if (event.custom_summary) {
          setStatus("reporting")
          try {
            // It might be a JSON string or raw text
            // We'll treat it as a single summary item to stream
            // Since buildPartialReport expects an array of JSON strings (as per agent output)
            // We can feed our cumulative summaries to it.

            // Check if it's valid JSON first
            let summaryStr = event.custom_summary
            if (typeof summaryStr !== 'string') {
              summaryStr = JSON.stringify(summaryStr)
            }

            // Quick check if it looks like our summary object
            if (summaryStr.includes("title") && summaryStr.includes("source")) {
              // Add to our temporary local summaries list (we need to track this state)
              // But handleResearch is async, state updates might be weird if we rely on setState inside loop
              // Better to keep a local variable in this scope?
              // No, we need to re-render. 

              // Actually, let's just append to the report directly or use buildPartialReport logic
              // But we don't have the previous summaries here easily unless we track local variable.

              // Strategy: accumulate locally and update
              allSummaries.push(summaryStr)
              const partialReport = buildPartialReport(req.query, allSummaries)
              setReport(partialReport)
              setLogs(prev => {
                const last = prev[prev.length - 1]
                if (last && last.startsWith("Streamed")) return prev // Debounce logs
                return [...prev, `Streamed summary item...`]
              })
            }
          } catch (e) {
            console.warn("Failed to parse streamed summary:", e)
          }
        }

        // 2. Handle Standard State Updates
        // LangGraph returns { nodeName: { key: value } } OR flattened from our new server logic
        const data = event.search || event.extract || event.summarize || event.report || event;

        if (data.report) {
          setReport(data.report)
          setStatus("completed")
          setLogs(prev => [...prev, "Report generation complete."])
        }

        if (data.search_results) {
          setStatus("extracting")
          setLogs(prev => [...prev, `Search found ${data.search_results.length} results.`])
        }
        if (data.contents) {
          setStatus("summarizing")
          setLogs(prev => [...prev, `Extracted content from ${data.contents.length} sources.`])
        }
        // Even if we stream individually, we might get the final batch 'summaries' list at the end of node
        if (data.summaries) {
          // We can overwrite with the authoritative list
          // Or just ignore if we trusted our streaming
          // Let's rely on streaming for UX, but final verify with this
          // buildPartialReport(req.query, data.summaries)
          setStatus("reporting")
          setLogs(prev => [...prev, `Generated ${data.summaries.length} summaries.`])

          // Build partial report from summaries for streaming effect
          try {
            // If we have custom_summary streaming, this might be redundant or overwrite.
            // For now, we'll keep it as a fallback/final update.
            const partialReport = buildPartialReport(req.query, data.summaries)
            setReport(partialReport)
          } catch (e) {
            console.error("Error building partial report:", e)
          }
        }
        if (data.message) {
          setLogs(prev => [...prev, data.message])
        }
      }

    } catch (error) {
      console.error("Research error:", error)
      setStatus("failed")
      setLogs(prev => [...prev, `Error: ${error}`])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-neutral-50 dark:bg-neutral-950 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">

        <ResearchForm onSubmit={handleResearch} isLoading={isLoading} />

        <div className="grid gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
          {logs.length > 0 && <LiveStatus logs={logs} status={status} />}

          {report && (
            <>
              <Separator />
              <ReportViewer markdown={report} />
            </>
          )}
        </div>

      </div>
    </main>
  )
}
