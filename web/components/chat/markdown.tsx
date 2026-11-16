import { Fragment, type ReactNode } from 'react'

type Props = {
  text: string
  /** Number of available sources; [n] beyond this stays plain text. */
  sourceCount?: number
  onCite?: (number: number) => void
}

/** Small dependency-free Markdown renderer: headings, lists, tables, bold, code, [n] citations. */
export function Markdown({ text, sourceCount = 0, onCite }: Props) {
  const lines = text.replace(/\r/g, '').split('\n')
  const blocks: ReactNode[] = []
  let index = 0

  const inline = (value: string, key: string): ReactNode[] =>
    value.split(/(\*\*[^*]+\*\*|`[^`]+`|\[\d+\])/g).map((part, i) => {
      const id = `${key}-${i}`
      if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
        return <strong key={id} className="font-semibold">{part.slice(2, -2)}</strong>
      }
      if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
        return <code key={id} className="rounded bg-muted px-1 py-0.5 text-[0.85em]">{part.slice(1, -1)}</code>
      }
      const cite = /^\[(\d+)\]$/.exec(part)
      if (cite && Number(cite[1]) >= 1 && Number(cite[1]) <= sourceCount) {
        const number = Number(cite[1])
        return (
          <button
            key={id}
            type="button"
            onClick={() => onCite?.(number)}
            className="mx-0.5 inline-flex size-[1.35em] -translate-y-px items-center justify-center rounded-md bg-accent align-baseline text-[0.7em] font-bold text-primary transition hover:bg-primary hover:text-primary-foreground"
            aria-label={`Xem nguồn ${number}`}
          >
            {number}
          </button>
        )
      }
      return <Fragment key={id}>{part}</Fragment>
    })

  const splitRow = (row: string) => row.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim())

  while (index < lines.length) {
    const line = lines[index]
    const key = `b${index}`

    if (!line.trim()) { index++; continue }

    const heading = /^(#{1,4})\s+(.*)$/.exec(line)
    if (heading) {
      blocks.push(<p key={key} className="mt-4 mb-1 text-[15px] font-semibold first:mt-0">{inline(heading[2], key)}</p>)
      index++
      continue
    }

    if (line.trim().startsWith('|') && /^\s*\|?\s*:?-{2,}/.test(lines[index + 1] ?? '')) {
      const header = splitRow(line)
      const rows: string[][] = []
      index += 2
      while (index < lines.length && lines[index].trim().startsWith('|')) rows.push(splitRow(lines[index++]))
      blocks.push(
        <div key={key} className="my-3 overflow-x-auto rounded-xl border">
          <table className="w-full border-collapse text-left text-[13px]">
            <thead className="bg-muted/70">
              <tr>{header.map((cell, i) => <th key={i} className="px-3 py-2 font-semibold">{inline(cell, `${key}h${i}`)}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, r) => (
                <tr key={r} className="border-t">
                  {row.map((cell, i) => <td key={i} className="px-3 py-2 align-top">{inline(cell, `${key}r${r}c${i}`)}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      )
      continue
    }

    const listMatch = /^\s*([-*•]|\d+[.)])\s+/.exec(line)
    if (listMatch) {
      const ordered = /\d/.test(listMatch[1])
      const items: string[] = []
      while (index < lines.length) {
        const m = /^\s*([-*•]|\d+[.)])\s+(.*)$/.exec(lines[index])
        if (!m || /\d/.test(m[1]) !== ordered) break
        items.push(m[2])
        index++
      }
      const List = ordered ? 'ol' : 'ul'
      blocks.push(
        <List key={key} className={`my-2 space-y-1.5 pl-5 ${ordered ? 'list-decimal' : 'list-disc'} marker:text-primary/60`}>
          {items.map((item, i) => <li key={i} className="pl-1">{inline(item, `${key}i${i}`)}</li>)}
        </List>,
      )
      continue
    }

    const paragraph: string[] = []
    while (index < lines.length && lines[index].trim() && !/^(#{1,4}\s|\s*([-*•]|\d+[.)])\s|\s*\|)/.test(lines[index])) {
      paragraph.push(lines[index++])
    }
    if (paragraph.length === 0) { paragraph.push(lines[index++]) }
    blocks.push(<p key={key} className="my-2 first:mt-0">{inline(paragraph.join(' '), key)}</p>)
  }

  return <div className="text-sm leading-7 text-foreground">{blocks}</div>
}
