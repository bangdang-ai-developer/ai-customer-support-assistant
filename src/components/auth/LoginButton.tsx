'use client'

import { signIn, signOut, useSession } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LogIn, LogOut, User, Settings, Crown, UserCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoginButtonProps {
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'sm' | 'default' | 'lg'
  className?: string
}

export function LoginButton({ variant = 'default', size = 'default', className }: LoginButtonProps) {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return (
      <Button variant="ghost" size={size} disabled className={className}>
        <User className="w-4 h-4 mr-2" />
        Loading...
      </Button>
    )
  }

  if (!session) {
    return (
      <Button 
        variant={variant} 
        size={size} 
        className={className}
        onClick={() => signIn()}
      >
        <LogIn className="w-4 h-4 mr-2" />
        Sign In
      </Button>
    )
  }

  const isAdmin = session.user?.role === 'admin'
  const isGuest = session.user?.role === 'guest'

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className={cn("relative h-8 w-8 rounded-full", className)}>
          <Avatar className="h-8 w-8">
            <AvatarImage src={session.user?.image || ''} alt={session.user?.name || ''} />
            <AvatarFallback className="bg-primary/10">
              {isGuest ? (
                <UserCircle className="h-4 w-4" />
              ) : (
                session.user?.name?.charAt(0)?.toUpperCase() || session.user?.email?.charAt(0)?.toUpperCase()
              )}
            </AvatarFallback>
          </Avatar>
          {isAdmin && (
            <Crown className="absolute -top-1 -right-1 h-3 w-3 text-yellow-500 bg-background rounded-full p-0.5" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {session.user?.name || 'Anonymous User'}
              {isAdmin && <span className="text-xs text-yellow-600 ml-1">(Admin)</span>}
              {isGuest && <span className="text-xs text-gray-500 ml-1">(Guest)</span>}
            </p>
            <p className="text-xs leading-none text-muted-foreground">
              {session.user?.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            <span>Profile</span>
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </DropdownMenuItem>
          {isAdmin && (
            <DropdownMenuItem>
              <Crown className="mr-2 h-4 w-4" />
              <span>Admin Panel</span>
            </DropdownMenuItem>
          )}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => signOut()}>
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}