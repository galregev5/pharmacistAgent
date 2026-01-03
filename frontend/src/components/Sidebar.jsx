import { Plus, UserRound, Clock3 } from 'lucide-react'
import { Button } from './ui/button'
import { ScrollArea } from './ui/scroll-area'
import { Separator } from './ui/separator'

const history = {
  today: ['Aspirin inquiry', 'Drug interaction check'],
  yesterday: ['Refill reminder setup', 'Budget update for stock'],
}

function HistoryGroup({ title, items }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 px-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        <Clock3 className="h-3 w-3" />
        <span>{title}</span>
      </div>
      <div className="space-y-1">
        {items.map((label) => (
          <Button
            key={label}
            variant="ghost"
            className="w-full justify-start text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {label}
          </Button>
        ))}
      </div>
    </div>
  )
}

function Sidebar() {
  return (
    <aside className="flex h-full w-64 flex-col border-r bg-slate-50">
      <div className="flex items-center justify-between border-b px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">PA</div>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-slate-900">Pharmacy Agent</p>
            <p className="text-xs text-slate-500">Medical SaaS Console</p>
          </div>
        </div>
        <Button variant="outline" size="sm" className="gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full space-y-4 px-3 py-4">
          <HistoryGroup title="Today" items={history.today} />
          <Separator className="my-2" />
          <HistoryGroup title="Yesterday" items={history.yesterday} />
        </ScrollArea>
      </div>

      <div className="border-t px-4 py-4">
        <Button variant="ghost" className="w-full justify-start gap-2 text-slate-700 hover:bg-slate-100">
          <UserRound className="h-4 w-4" />
          Settings
        </Button>
      </div>
    </aside>
  )
}

export default Sidebar
