import { useUser } from '@/utils/useUser'
import { useRouter } from 'next/router'
import { useState } from 'react'
import Dashboard from '../../components/Dashboard'
import { Plan, tiers } from '../../components/PricingSection'
import Spinner from '../../components/Spinner'

import { camelize, postData } from '@/utils/helpers'
import { getStripe } from '@/utils/stripe-client'

import { PrimaryButton } from '@/components/Button'
import Usage, { UsageItem } from '@/components/Usage'
import { Price } from '@/utils/types'
import { createServerSupabaseClient } from '@supabase/auth-helpers-nextjs'

const FreePlan = () => {
  const { subscription } = useUser()
  return <Plan tier={tiers[0]}>{ }</Plan>
}

const ProPlan = () => {
  const router = useRouter()
  const [priceIdLoading, setPriceIdLoading] = useState<string>()
  const { user, subscription } = useUser()

  const handleCheckout = async (price: Price) => {
    setPriceIdLoading(price.id)
    if (subscription) {
      return router.push('/dashboard')
    }

    try {
      const { sessionId } = await postData({
        url: '/api/create-checkout-session',
        data: { price },
      })

      const stripe = await getStripe()
      stripe?.redirectToCheckout({ sessionId })
    } catch (error) {
      return alert((error as Error)?.message)
    } finally {
      setPriceIdLoading(undefined)
    }
  }
  return (
    <Plan tier={tiers[1]}>
      <PrimaryButton
        onClick={() => handleCheckout(tiers[1])}
        className="flex w-full items-center justify-center gap-3 py-3 font-semibold"
      >
        {priceIdLoading && (
          <>
            Upgrading...
            <Spinner />
          </>
        )}
        {!priceIdLoading && subscription?.status === 'active' && 'Manage plan'}
        {!priceIdLoading && subscription?.status !== 'active' && 'Upgrade'}
      </PrimaryButton>
    </Plan>
  )
}

const EnterprisePlan = () => {
  return (
    <Plan tier={tiers[2]}>
      <a
        href="https://cal.com/potato/20min?duration=20"
        target="_blank"
        rel="noreferrer"
      >
        <PrimaryButton className="flex w-full items-center justify-center gap-3 py-3 font-semibold">
          Contact us
        </PrimaryButton>
      </a>
    </Plan>
  )
}

export default function Index({ usage }: { usage: UsageItem[] }) {
  const user = useUser()
  const limit = (user?.subscription?.price_id && tiers.find((t) =>
    t.id == user?.subscription?.price_id
  )?.playgroundLimit) || 5

  return (
    <Dashboard>
      <div className="mt-6 flex flex-col gap-8">
        <Usage usage={usage} limit={limit} />
        <div className="rounded-2xl bg-gray-100 py-5 px-5">
          {/* add info text about pricing page somehting like hi wleocme to pcicing page you can downgrad e ugprade or you can manage your account here */}
          <h3 className="mb-6 text-2xl font-semibold">Account</h3>
          <p className="mb-3 text-gray-500">
            You can manage you subscription here. Easily upgrade, downgrade or
            cancel your subscription.
          </p>

          {user?.subscription?.status === 'active' && (
            <a
              href={process.env.NEXT_PUBLIC_STRIPE_CUSTOMER_PORTAL}
              target="_blank"
              rel="noreferrer"
            >
              <PrimaryButton className="mx-auto flex w-1/4 items-center justify-center">
                Manage my subscription
              </PrimaryButton>
            </a>
          )}
        </div>

        <div className="mx-auto grid max-w-md grid-cols-1 gap-4 lg:max-w-5xl lg:grid-cols-3 lg:gap-4">
          <FreePlan />
          <ProPlan />
          <EnterprisePlan />
        </div>
      </div>
    </Dashboard>
  )
}

export const getServerSideProps = async (ctx) => {
  const supabase = createServerSupabaseClient(ctx)

  // Check if we have a session
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session)
    return {
      redirect: {
        destination: '/login',
        permanent: false,
      },
    }

  // todo limit to 30 days
  let { data, status, error } = await supabase
    .from('plan_usages')
    .select('*')
    .eq('user_id', session.user.id)

  if (error) {
    console.log(error)
  }

  data = camelize(data)

  console.log(data, session.user.id)

  return {
    props: {
      initialSession: session,
      user: session.user,
      usage: data,
    },
  }
}

