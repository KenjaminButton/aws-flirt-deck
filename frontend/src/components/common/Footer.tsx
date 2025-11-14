/**
 * Footer Component
 * 
 * Simple footer with contact information for MVP
 * Displays at bottom of all pages
 */

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Left: Branding */}
          <div className="text-center md:text-left">
            <p className="text-gray-600 text-sm">
              💕 <span className="font-semibold">FlirtDeck</span> - Keep the conversation flowing
            </p>
          </div>

          {/* Center: Contact */}
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              Questions or feedback?{' '}
              <a 
                href="mailto:support@flirtdeck.com"
                className="text-purple-600 hover:text-purple-700 font-medium underline"
              >
                support@flirtdeck.com
              </a>
            </p>
          </div>

          {/* Right: Copyright */}
          <div className="text-center md:text-right">
            <p className="text-gray-500 text-xs">
              © {new Date().getFullYear()} FlirtDeck. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;